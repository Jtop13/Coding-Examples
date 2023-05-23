import requests
import time
from bs4 import BeautifulSoup


def fetch_all():

    exchanges = ['NASDAQ', 'NYSE', 'AMEX']
    ticker_symbols = []
    start_time = time.time()

    for exchange in exchanges:
        page = 1
        while True:
            url = f'https://eoddata.com/stocklist/{exchange}/{chr(64 + page)}.htm'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "No symbols found" in response.text:
                break

            table = soup.find('table', {'class': 'quotes'})
            if table:
                rows = table.findAll('tr')
                for row in rows[1:]:  # Skip the header row
                    cells = row.findAll('td')
                    ticker = cells[0].text.strip()
                    ticker_symbols.append(ticker)
                    #print(ticker)
            else:
                break

            page += 1

    # Remove duplicates by converting the list to a set and then back to a list
    ticker_symbols = list(set(ticker_symbols))

    print(ticker_symbols)
    print(len(ticker_symbols))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"The program took {elapsed_time} seconds to execute.")
    
    return ticker_symbols


