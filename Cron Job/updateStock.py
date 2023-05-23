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