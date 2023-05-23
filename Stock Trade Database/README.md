This project is for a database I
created using PSQL where the
purpose was to create a website that
allowed users to create and track
portfolios that they created using 
daily live stock data.

The png files show images of the relational schema
and EER diagrams of the database that are good practice
for implementing the concepts into code.


The files fetch_all.py and stock_scrapper.py were used
to populate the database with stock names and prices over
the past year. Using yfinance library we were able to 
scrape 2.5 million daily values from over 10,000 different 
companies.

The files g04econ.py and route_accounts.py were used
to lauch the database into a websever and demenstrate how
I pulled data from the database and communicated with
javascript. Route accounts is in isolation and a seperate file
in order to manage the login and register of users. 