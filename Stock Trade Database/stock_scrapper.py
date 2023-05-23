import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from psycopg2 import connect
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from fetch_all import *
import requests.exceptions


# Replace these with your own database credentials
db_config = {
    'dbname': 'my_db',
    'user': 'g04ec0n',
    'password': 'g04ec0n'
}



"""def fetch_500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    sp500_table = tables[0]
    symbols = sp500_table['Symbol'].tolist()

    return symbols"""

# Add your list of stock symbols
stocks_to_track = fetch_all()

def fetch_and_store_stock_data(stock_symbols):
    db = connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        cursor_factory=DictCursor
    )
    cursor = db.cursor()
    
    #clear out database
    cursor.execute("DELETE FROM historical_values")
    cursor.execute("DELETE FROM stock")
    
    # Get stock data for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    for symbol in stock_symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            
            print(stock)
            
            if hist.empty:
                raise KeyError("No data available or stock may be delisted") 
                
            # Insert stock data into the stock table if not exists
            cursor.execute("INSERT INTO stock (tickerSymbol, company_name) VALUES (%s, %s) ON CONFLICT (tickerSymbol) DO NOTHING", (symbol, stock.info['shortName']))


            # Insert historical data into the historical_values table
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
    # Commit the changes to the database
    db.commit()
    db.close()


start_time = time.time()
#call fetch
fetch_and_store_stock_data(stocks_to_track)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"The program took {elapsed_time} seconds to execute.")



