import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import os
sys.path.insert(0, '/home/g04ec0n/public_html/wsgi')
from route_accounts import *
from flask import Flask, render_template, session, request, redirect, \
                  url_for, g, flash



import time
import pandas as pd
from datetime import datetime, timedelta
import requests.exceptions
from flask import jsonify #only using this for optimal search bar technique 

import threading
lock = threading.Lock()

# connect is used to connect to a PostgreSQL database.

from psycopg2 import connect

# DictCursor allows us to work with the results returned by fetc
# operations on a cursor as if they were stored in a dictionary, rather
# than a tuple.  tuple access via an index is still possible.

from psycopg2.extras import DictCursor


# As necessary, add variable definitions to your cs417secrets.py file.
# Remember, they should have the form
#     DBDEMO_DB = 'registration'
# These definitions will be stored in the app.config object as dictionary
# key and value pairs.  See below.

app = Flask(__name__, static_folder='static')
app.config.from_pyfile('config.py')

#print(app.config)
# This decorator is used to register a function to be called first during
# the request.  Use it to establish session initialization.  The registered
# function should be parameterless.

@app.before_request
def beforeReq():
    if 'loggedIn' not in session:
        session['loggedIn'] = False
        session.modified = True


# This decorator is used to register a function to be called once the
# request is completed.  Use it to clean-up at the end of a request.  The
# registered function takes a response object parameter and returns a response
# object.

@app.after_request
def afterReq(response):
    closeDb()
    return response


# Get the connection to the back-end db.  If the connection doesn't yet
# exist, create it.  Note how to access your application "secrets" via
# the app.config dictionary.

def getDb():
    if 'db' not in g:
        g.db = connect(dbname=app.config['MY_DB'],
                       user=app.config['DB_USER'],
                       password=app.config['DB_PW'],
                       cursor_factory=DictCursor)
    return g.db


def closeDb():
    db = g.pop('db', None)
    if db is not None:
        db.close()


#@app.route('/')
#def home():
#    return render_template('indexWeb.html')




def updateStocks():
    #insure only one person can update the stocks so multiple requests can't be made
    lock.acquire()
    
    db = getDb()
    cursor = db.cursor()
    # Get the most recent date-time value from the events table
    cursor.execute("SELECT MAX(lasttime) FROM updateHist")
    result = cursor.fetchone()
    last_update = result[0]

    # If there is no previous date value, assume that all data is new
    if last_update is None:
        start_date = (datetime.now() - timedelta(days=365)).date()
    else:
        start_date = last_update.date()

    # Get the current date
    end_date = datetime.now().date()
    
    # Check if the current date matches the last update date
    if end_date == start_date:
        lock.release()
        return

    # Get the list of stock symbols from the stock table
    cursor.execute("SELECT tickerSymbol FROM stock")
    symbols = cursor.fetchall()
    
    updated_symbols = 0
    total_symbols = len(symbols)
    
    # For each stock symbol, fetch the latest data and store it in the historical_values table
    for symbol in symbols:

        
        symbol = symbol[0]
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            
            # Insert the latest data into the historical_values table
            for date, row in hist.iterrows():
                daily_change = row['Close'] - row['Open']
                cursor.execute("INSERT INTO historical_values (dailyChange, price, date, tickerSymbol) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (daily_change, row['Close'], date.date(), symbol))
        except KeyError as e:
            print(f"Error processing symbol {symbol}: {e}")
        except TypeError as e:
            print(f"Error inputing symbol {symbol}: {e}")
        except IndexError as e:
            print(f"Error processing symbol {symbol}: {e}")
        except requests.exceptions.ReadTimeout as e:
            print(f"Error processing symbol {symbol}: {e}")
        
        updated_symbols += 1
        percent_completed = (updated_symbols / total_symbols) * 100
        print("{}% completed".format(percent_completed))
    # Store the current date-time in the events table
    cursor.execute("INSERT INTO updateHist (lasttime) VALUES (%s)", (end_date,))

    # Commit the changes to the database
    db.commit()

    lock.release()
    return

@app.route('/updateStocks')
def updatePage():
    updateStocks()
    return render_template('update.html')

@app.route('/')
def home():
    session['redirectPortfolio'] = False
    return render_template('home.html')
    #SPY
''' 
    symbol = "^GSPC"
    data = yf.download(symbol, start="2022-04-25", end="2023-04-25")
    fig = plt.figure()
    plt.plot(data['Close'])
    plt.title(f'{symbol} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    spy = f"static/{symbol}_price.png"
    spyPath = f"/home/g04ec0n/public_html/wsgi/{spy}"
    fig.savefig(spyPath, format='png')
    
    #DJI 
    jones = "^DJI"
    data = yf.download(jones, start="2022-04-25", end="2023-04-25")
    fig = plt.figure()
    plt.plot(data['Close'])
    plt.title(f'{jones} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    dji = f"static/{jones}_price.png"
    djiPath = f"/home/g04ec0n/public_html/wsgi/{dji}"
    fig.savefig(djiPath, format='png')
    
    #NASDAQ 
    nasdaq = "^IXIC"
    data = yf.download(nasdaq, start="2022-04-25", end="2023-04-25")
    fig = plt.figure()
    plt.plot(data['Close'])
    plt.title(f'{nasdaq} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price')
    NAS = f"static/{nasdaq}_price.png"
    nasPath = f"/home/g04ec0n/public_html/wsgi/{NAS}"
    fig.savefig(nasPath, format='png')'''
        
    
    #return render_template('home.html', spyPath=spy,djiPath=dji, nasPath = NAS)
    #return render_template('design.html')
    #render_template('loading.html')
    
   


@app.route('/stock_list')
def stock_list():
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT tickerSymbol, company_name FROM stock ORDER BY tickerSymbol")
    stocks = cursor.fetchall()
    return render_template('stock_list.html', stocks=stocks)
    

@app.route('/api/stocks')
def api_stocks():
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT tickerSymbol, company_name FROM stock ORDER BY tickerSymbol")
    stocks = cursor.fetchall()
    stocks_list = [{'tickerSymbol': stock[0], 'company_name': stock[1]} for stock in stocks]
    return jsonify(stocks_list)


@app.route('/portfolio')
def portfolio():
    if session['loggedIn'] == True:
        db = getDb()
        cur = db.cursor()

        # Fetch portfolios
        cur.execute("""
            SELECT portId, name, budget
            FROM portfolio
            WHERE username = %s
            ORDER BY name
        """, (session['user'],))
        portfolios = [dict(portId=row[0], name=row[1], budget=row[2]) for row in cur.fetchall()]
        print(portfolios)
        # For each portfolio, fetch holdings and latest stock values
        for portfolio in portfolios:
            cur.execute("""
                SELECT h.tickerSymbol, s.company_name, h.quantity, hv.price as latest_price
                FROM holdings h
                INNER JOIN stock s ON h.tickerSymbol = s.tickerSymbol
                INNER JOIN (
                    SELECT tickerSymbol, MAX(date) as latest_date 
                    FROM historical_values 
                    GROUP BY tickerSymbol
                ) hv_max ON s.tickerSymbol = hv_max.tickerSymbol
                INNER JOIN historical_values hv ON hv.tickerSymbol = hv_max.tickerSymbol AND hv.date = hv_max.latest_date
                WHERE h.portId = %s
            """, (portfolio['portId'],))
            result = cur.fetchall()
            #print(result)
            #portfolio['holdings'] = [dict(tickerSymbol=row[0], company_name=row[1], quantity=row[2], latest_price=row[3]) for row in cur.fetchall()] if result else []
            portfolio['holdings'] = result
            #print(portfolio)
        #print(portfolios)
        
        return render_template('portfolio.html', portfolios=portfolios)
    else:
        session['redirectPortfolio'] = True
        return redirect(url_for('login'))



    
import re    
    
@app.route('/create_portfolio', methods=['GET', 'POST'])
def create_portfolio():
    if session['loggedIn'] == True:
        if request.method == 'POST':
            name = request.form['name']
            budget = int(float(request.form['budget']))
            end_date = request.form['end_date']
            username = session.get('user')

            # Check if user is not logged in
            if username is None:
                return render_template('create_portfolio.html', error="ERROR: You must be logged in to create a portfolio!")


            # Check if name is empty
            if name == '':
                return render_template('create_portfolio.html', error="ERROR: Must fill out name!")

            # Check for no special characters except spaces
            if not re.match("^[a-zA-Z0-9 ]+$", name):
                return render_template('create_portfolio.html', error="ERROR: Name must contain only letters, numbers, or spaces!")

            # Check if budget is empty
            if budget == '':
                return render_template('create_portfolio.html', error="ERROR: Must fill out budget!")

            # Check if end_date is empty
            if end_date == '':
                return render_template('create_portfolio.html', error="ERROR: Must fill out end date!")

            # Check if name is too large
            if len(name) > 64:
                return render_template('create_portfolio.html', error="ERROR: Name is too long!")
                
                    # Convert end_date_str to a datetime.date object
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            # Check if the end_date exists within the range of historical_values dates in the database
            with getDb().cursor() as cur:
                cur.execute('SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM historical_values;')
                date_range = cur.fetchone()
                min_date = date_range['min_date']
                max_date = date_range['max_date']

            if not min_date <= end_date <= max_date:
                return render_template('create_portfolio.html', error="ERROR: End date must be within the range of historical values dates in the database!")

            # Check if the budget is a positive number
            if budget <= 0:
                return render_template('create_portfolio.html', error="ERROR: Budget must be a positive number!")

            with getDb().cursor() as cur:
                # Check if a portfolio with the same name already exists for the user
                query = 'SELECT name FROM portfolio WHERE username=%(username)s AND name=%(name)s;'
                vars = {'username': username, 'name': name}
                cur.execute(query, vars)
                result = cur.fetchone()
                getDb().commit()

                if result is not None:
                    return render_template('create_portfolio.html', error="ERROR: You already have a portfolio named that!")
                else:
                    cur.execute(
                        """INSERT INTO portfolio (name, budget, end_date, username) VALUES (%s, %s, %s, %s)""",
                        (name, budget, end_date, username)
                    )
                    getDb().commit()

            return redirect(url_for('portfolio'))  # Redirect the user to the portfolios page or another appropriate page
        else:
            return render_template('create_portfolio.html')

    else:
        session['redirectPortfolio'] = True
        return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    return register_route(request, session,redirect, url_for, getDb)


@app.route('/logout', methods = ['POST'])
def logout():
    return logout_route(session, redirect, url_for)


@app.route('/login', methods = ['POST', 'GET'])
def login():
    return login_route(request, session,redirect, url_for, getDb)

from datetime import timedelta

"""@app.route('/prices', methods=['POST', 'GET'])
def prices():
    if request.method == 'POST':
        symbol = request.form['symbol']
    elif request.method == 'GET':
        symbol = request.args.get('symbol')
    else:
        return render_template('error.html', message="Invalid request method")

    # Check if the symbol parameter is provided
    if not symbol:
        return render_template('error.html', message="No symbol provided")
    
    # Fetch historical prices from the database
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT price, date FROM historical_values WHERE tickerSymbol = %s ORDER BY date", (symbol,))
    historical_prices = cursor.fetchall()

    # Check if historical_prices is empty
    if not historical_prices:
        return render_template('error.html', message=f"No historical data found for symbol {symbol}")

    # Extract dates and prices from the fetched data
    dates = [row['date'] for row in historical_prices]
    prices = [row['price'] for row in historical_prices]
    
    
    # Get the days parameter or use the default 30 days
    days = request.args.get('days', default=365, type=int)


    
    # Filter dates and prices for the last N days
    start_date = dates[-1] - timedelta(days=days)
    filtered_dates = [date for date in dates if date >= start_date]
    filtered_prices = prices[-len(filtered_dates):]
    
    # Calculate the moving average
    period = min(days,30)
    ma = []
    for i in range(period - 1, len(filtered_prices)):
        ma.append(sum(filtered_prices[i - period + 1:i + 1]) / period)

    # Plot stock prices and moving average
    plt.plot(filtered_dates, filtered_prices, label=symbol)
    plt.plot(filtered_dates[period - 1:], ma, label=f"{symbol} {period}-day MA")
    plt.title(f"Stock prices and {period}-day MA for {symbol}")
    
    # Format x-axis labels
    interval = max(1, int(days/8))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval)) 
    
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    #ma_path = f"static/{symbol}_ma_{period}.png"
    ma_path = f"static/{symbol}.png"
    MAfile_path = f"/home/g04ec0n/public_html/wsgi/{ma_path}"
    if os.path.exists(MAfile_path):
        os.remove(MAfile_path)
    plt.savefig(MAfile_path)
    os.chmod(MAfile_path, 0o666)
    plt.clf() 

    # Fetch stock information from the database
    cursor.execute("SELECT company_name FROM stock WHERE tickerSymbol = %s", (symbol,))
    company_name = cursor.fetchone()
    
    if company_name:
        info = f"Company name: {company_name['company_name']}"
    else:
        info = f"No information found for symbol {symbol}"

    return render_template('prices.html', symbol=symbol, info=info, ma_path=ma_path)"""

@app.route('/prices', methods=['POST', 'GET'])
def prices():
    logged_in = False
    if 'user' in session:
        logged_in = True
        username = session['user']
    
    db = getDb()
    cursor = db.cursor()
    
    if request.method == 'POST':
        if logged_in:
            symbol = request.form['symbol']
            portId = request.form.get('portId', None)  # Get the selected portfolio ID from the form
            if not portId:
                return render_template('error.html', message="No portfolio selected")
            portId = int(portId)  # Convert the selected portfolio ID to an integer

            quantity = int(request.form['quantity'])
            date = request.form['date']

            cursor.execute("SELECT budget FROM portfolio WHERE portId = %s", (portId,))
            budget = cursor.fetchone()['budget']

            cursor.execute("SELECT price FROM historical_values WHERE tickerSymbol = %s AND date = %s", (symbol, date))
            price = cursor.fetchone()['price']

            total_cost = price * quantity

            if budget < total_cost:
                return render_template('error.html', message="Insufficient budget for this transaction")

            if datetime.strptime(date, '%Y-%m-%d').date() > datetime.now().date():
                return render_template('error.html', message="Cannot purchase stock before end date")

            # Update the budget and add the stock to the holdings table
            new_budget = budget - total_cost
            cursor.execute("UPDATE portfolio SET budget = %s WHERE portId = %s", (new_budget, portId))

            cursor.execute("INSERT INTO holdings (portId, tickerSymbol, quantity) VALUES (%s, %s, %s) ON CONFLICT (portId, tickerSymbol) DO UPDATE SET quantity = holdings.quantity + %s", (portId, symbol, quantity, quantity))

            # Record the transaction in the transaction table
            cursor.execute("INSERT INTO transaction (date, portId) VALUES (%s, %s) RETURNING transId", (date, portId))
            transId = cursor.fetchone()[0]
            result = cursor.fetchone()
            print(transId)

            # Include the trade in the trades table
            cursor.execute("INSERT INTO trades (transId, type, quantity, tickerSymbol) VALUES (%s, 'Buy', %s, %s)", (transId, quantity, symbol))

            db.commit()
            
            return redirect(url_for('portfolio'))

    # ... (keep the existing code for handling GET requests)
    if request.method == 'GET':
        symbol = request.args.get('symbol')

    # Check if the symbol parameter is provided
    if not symbol:
        return render_template('error.html', message="No symbol provided")
    
    # Fetch historical prices from the database
    cursor.execute("SELECT price, date FROM historical_values WHERE tickerSymbol = %s ORDER BY date", (symbol,))
    historical_prices = cursor.fetchall()

    # Check if historical_prices is empty
    if not historical_prices:
        return render_template('error.html', message=f"No historical data found for symbol {symbol}")

    # Extract dates and prices from the fetched data
    dates = [row['date'] for row in historical_prices]
    prices = [row['price'] for row in historical_prices]

    # Get the days parameter or use the default 30 days
    days = request.args.get('days', default=365, type=int)

    # Filter dates and prices for the last N days
    start_date = dates[-1] - timedelta(days=days)
    filtered_dates = [date for date in dates if date >= start_date]
    filtered_prices = prices[-len(filtered_dates):]

    # Calculate the moving average
    period = min(days,30)
    ma = []
    for i in range(period - 1, len(filtered_prices)):
        ma.append(sum(filtered_prices[i - period + 1:i + 1]) / period)

    # Plot stock prices and moving average
    plt.plot(filtered_dates, filtered_prices, label=symbol)
    plt.plot(filtered_dates[period - 1:], ma, label=f"{symbol} {period}-day MA")
    plt.title(f"Stock prices and {period}-day MA for {symbol}")
    
    # Format x-axis labels
    interval = max(1, int(days/8))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval)) 

    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()

    ma_path = f"static/{symbol}.png"
    MAfile_path = f"/home/g04ec0n/public_html/wsgi/{ma_path}"
    if os.path.exists(MAfile_path):
        os.remove(MAfile_path)
    plt.savefig(MAfile_path)
    os.chmod(MAfile_path, 0o666)
    plt.clf() 

    # Fetch stock information from the database
    cursor.execute("SELECT company_name FROM stock WHERE tickerSymbol = %s", (symbol,))
    company_name = cursor.fetchone()

    if company_name:
        info = f"Company name: {company_name['company_name']}"
    else:
        info = f"No information found for symbol {symbol}"

    portfolios = []
    if logged_in:
        cursor.execute("SELECT portId, name, budget FROM portfolio WHERE username = %s", (username,))
        portfolios = cursor.fetchall()
        # Convert portfolios to a list of dictionaries
        portfolios = [{'portId': port[0], 'name': port[1], 'budget': port[2]} for port in portfolios]

    return render_template('prices.html', symbol=symbol, info=info, ma_path=ma_path, logged_in=logged_in, portfolios=portfolios, min_date=min(dates), max_date=max(dates))


    
"""@app.route('/prices', methods=['POST', 'GET'])
def prices():
    logged_in = False
    if 'user' in session:
        logged_in = True
        username = session['user']
    
    if request.method == 'POST':
        symbol = request.form['symbol']
    elif request.method == 'GET':
        symbol = request.args.get('symbol')
    else:
        return render_template('error.html', message="Invalid request method")

    # Check if the symbol parameter is provided
    if not symbol:
        return render_template('error.html', message="No symbol provided")
    
    # Fetch historical prices from the database
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT price, date FROM historical_values WHERE tickerSymbol = %s ORDER BY date", (symbol,))
    historical_prices = cursor.fetchall()

    # Check if historical_prices is empty
    if not historical_prices:
        return render_template('error.html', message=f"No historical data found for symbol {symbol}")

    # Extract dates and prices from the fetched data
    dates = [row['date'] for row in historical_prices]
    prices = [row['price'] for row in historical_prices]
    
    
    # Get the days parameter or use the default 30 days
    days = request.args.get('days', default=365, type=int)


    
    # Filter dates and prices for the last N days
    start_date = dates[-1] - timedelta(days=days)
    filtered_dates = [date for date in dates if date >= start_date]
    filtered_prices = prices[-len(filtered_dates):]
    
    # Calculate the moving average
    period = min(days,30)
    ma = []
    for i in range(period - 1, len(filtered_prices)):
        ma.append(sum(filtered_prices[i - period + 1:i + 1]) / period)

    # Plot stock prices and moving average
    plt.plot(filtered_dates, filtered_prices, label=symbol)
    plt.plot(filtered_dates[period - 1:], ma, label=f"{symbol} {period}-day MA")
    plt.title(f"Stock prices and {period}-day MA for {symbol}")
    
    # Format x-axis labels
    interval = max(1, int(days/8))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval)) 
    
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    #ma_path = f"static/{symbol}_ma_{period}.png"
    ma_path = f"static/{symbol}.png"
    MAfile_path = f"/home/g04ec0n/public_html/wsgi/{ma_path}"
    if os.path.exists(MAfile_path):
        os.remove(MAfile_path)
    plt.savefig(MAfile_path)
    os.chmod(MAfile_path, 0o666)
    plt.clf() 

    # Fetch stock information from the database
    cursor.execute("SELECT company_name FROM stock WHERE tickerSymbol = %s", (symbol,))
    company_name = cursor.fetchone()
    
    if company_name:
        info = f"Company name: {company_name['company_name']}"
    else:
        info = f"No information found for symbol {symbol}"
    
    # ... (keep the existing code for fetching historical prices and plotting)

    portfolios = []
    if logged_in:
        cursor.execute("SELECT portId, name, budget FROM portfolio WHERE username = %s", (username,))
        portfolios = cursor.fetchall()
        # Convert portfolios to a list of dictionaries
        portfolios = [{'portId': port[0], 'name': port[1], 'budget': port[2]} for port in portfolios]

        #print(portfolios)

        if request.method == 'POST' and logged_in and portfolios:
            symbol = request.form['symbol']
            portId = request.form.get('portId', None)  # Get the selected portfolio ID from the form
            #print(request.form)
            #print(portId)
            if not portId:
                return render_template('error.html', message="No portfolio selected")
            portId = int(portId)  # Convert the selected portfolio ID to an integer

            quantity = int(request.form['quantity'])
            date = request.form['date']
             
            
             
            cursor.execute("SELECT budget FROM portfolio WHERE portId = %s", (portId,))
            budget = cursor.fetchone()['budget']

            cursor.execute("SELECT price FROM historical_values WHERE tickerSymbol = %s AND date = %s", (symbol, date))
            price = cursor.fetchone()['price']

            total_cost = price * quantity

            if budget < total_cost:
                return render_template('error.html', message="Insufficient budget for this transaction")

            if datetime.strptime(date, '%Y-%m-%d').date() > datetime.now().date():
                return render_template('error.html', message="Cannot purchase stock before end date")

            # Update the budget and add the stock to the holdings table
            new_budget = budget - total_cost
            cursor.execute("UPDATE portfolio SET budget = %s WHERE portId = %s", (new_budget, portId))

            cursor.execute("INSERT INTO holdings (portId, tickerSymbol, quantity) VALUES (%s, %s, %s) ON CONFLICT (portId, tickerSymbol) DO UPDATE SET quantity = holdings.quantity + %s", (portId, symbol, quantity, quantity))

            # Record the transaction in the transaction table
            cursor.execute("INSERT INTO transaction (date, portId) VALUES (%s, %s) RETURNING transId", (date, portId))
            transId = cursor.fetchone()[0]
            result = cursor.fetchone()
            print(transId)

            # Include the trade in the trades table
            cursor.execute("INSERT INTO trades (transId, type, quantity, tickerSymbol) VALUES (%s, 'Buy', %s, %s)", (transId, quantity, symbol))

            db.commit()
        
    #flash('Transaction Complete')

    return render_template('prices.html', symbol=symbol, info=info, ma_path=ma_path, logged_in=logged_in, portfolios=portfolios, min_date=min(dates), max_date=max(dates))"""




#DO NOT DELETE OLD PRICES BUT STILL USEFULL
"""@app.route('/prices', methods=['POST', 'GET'])
def prices():
    if request.method == 'POST':
        symbol = request.form['symbol']
    elif request.method == 'GET':
        symbol = request.args.get('symbol')
    else:
        return render_template('error.html', message="Invalid request method")

    # Check if the symbol parameter is provided
    if not symbol:
        return render_template('error.html', message="No symbol provided")
    
    # Fetch historical prices from the database
    db = getDb()
    cursor = db.cursor()
    cursor.execute("SELECT price, date FROM historical_values WHERE tickerSymbol = %s ORDER BY date", (symbol,))
    historical_prices = cursor.fetchall()

    # Check if historical_prices is empty
    if not historical_prices:
        return render_template('error.html', message=f"No historical data found for symbol {symbol}")

    # Extract dates and prices from the fetched data
    dates = [row['date'] for row in historical_prices]
    prices = [row['price'] for row in historical_prices]

    # Calculate the moving average
    period = 30
    ma = []
    for i in range(period - 1, len(prices)):
        ma.append(sum(prices[i - period + 1:i + 1]) / period)

    # Plot stock prices and moving average
    #plt.plot(dates[period - 1:], prices[period - 1:], label=symbol)
    plt.plot(dates, prices, label=symbol)
    plt.plot(dates[period - 1:], ma, label=f"{symbol} {period}-day MA")
    plt.title(f"Stock prices and {period}-day MA for {symbol}")
    
    # Format x-axis labels
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=45)) 
    
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    ma_path = f"static/{symbol}_ma_{period}.png"
    MAfile_path = f"/home/g04ec0n/public_html/wsgi/{ma_path}"
    if os.path.exists(MAfile_path):
        os.remove(MAfile_path)
    plt.savefig(MAfile_path)
    os.chmod(MAfile_path, 0o666)
    plt.clf() 

    # Fetch stock information from the database
    cursor.execute("SELECT company_name FROM stock WHERE tickerSymbol = %s", (symbol,))
    company_name = cursor.fetchone()
    
    if company_name:
        info = f"Company name: {company_name['company_name']}"
    else:
        info = f"No information found for symbol {symbol}"

    return render_template('prices.html', symbol=symbol, info=info, ma_path=ma_path)"""





#@app.route('/process_selection')
#def process_selection():
    # Process the selected option and redirect to the appropriate page
 #   return redirect(url_for('some_view'))

    
@app.route('/stock')
def stock():
    return render_template('stock.html')
    
@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/personalInfo')
def personalInfo():
    return render_template('personalInfo.html')

if __name__ != '__main__':
    application = app
