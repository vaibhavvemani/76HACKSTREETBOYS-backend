import sqlite3
import requests
# from datetime import datetime

key = "TUC0K41N3AORJJ1W"

def fetch_daily_data(ticker): 
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={key}'
    result = requests.get(url)
    return result.json()

def fetch_fund_holdings(ticker):
    url = f'https://www.alphavantage.co/query?function=ETF_PROFILE&symbol={ticker}&apikey={key}'
    result = requests.get(url)
    return result.json()

def store_data(ticker, data):

    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()
    daily_series = data.get("Time Series (Daily)", {})

    if not daily_series:
        return 404;

    for date, values in daily_series.items():
        cursor.execute("""
            INSERT OR IGNORE INTO fund_prices (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            date,
            float(values["1. open"]),
            float(values["2. high"]),
            float(values["3. low"]),
            float(values["4. close"]),
            int(values["5. volume"])
        ))

    conn.commit()
    conn.close()

    print(f"stored data for {ticker}")
    return 200

def store_holdings(ticker, data):

    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()

    sectors = data.get("sectors", [])
    holdings = data.get("holdings", [])

    if not holdings:
        return 405

    for sector in sectors:
        cursor.execute("""
            insert or ignore into fund_sectors (ticker, sector, weight)
            values (?, ?, ?)
        """, (ticker, sector["sector"], float(sector["weight"])))

    for holding in holdings:
        cursor.execute("""
            insert or ignore into fund_holdings (ticker, company_name, company_ticker, weight)
            values (?, ?, ?, ?)
        """, (ticker, holding["description"], holding["symbol"], float(holding["weight"] ))
        )

    conn.commit()
    conn.close()

    print("holdings and sectors added to the db")
    return 200


def check_if_exists(ticker):
    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()

    # today = datetime.today().strftime("%Y-%m-%d")
    #
    # cursor.execute("""
    #     select 1 from fund_prices 
    #     where ticker = ? and date = ? 
    #     limit 1
    # """, (ticker, today, ))

    cursor.execute("""
        select 1 from fund_prices 
        where ticker = ?
        limit 1
    """, (ticker,))

    funds_exists = cursor.fetchone()

    if funds_exists:
        print("fund exists in the table")
    else:
        result = fetch_daily_data(ticker)

        if "Time Series (Daily)" in result:
            store_data(ticker, result)
        else:
            print("!!! Alpha Vantage returned no data")

    cursor.execute("""
        select 1 from fund_holdings
        where ticker = ?
        limit 1
    """, (ticker, ))

    holdings_exists = cursor.fetchone()

    if holdings_exists:
        print("holdings exists in the table")
    else:
        result = fetch_fund_holdings(ticker)
        store_holdings(ticker, result)

    conn.close()

def retrieve_data(ticker):
    check_if_exists(ticker)
    fund_prices = []
    fund_holdings = []
    fund_sectors = []
    
    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()

    cursor.execute("select * from fund_prices where ticker = ?", (ticker, ))

    fund_prices = cursor.fetchall()

    cursor.execute("select * from fund_holdings where ticker = ? order by weight desc limit 50", (ticker, ))

    fund_holdings = cursor.fetchall()

    cursor.execute("select * from fund_sectors where ticker = ? order by weight desc limit 50", (ticker, ))

    fund_sectors = cursor.fetchall()

    combined = {
        "fund_prices": fund_prices,
        "fund_holdings": fund_holdings,
        "fund_sectors": fund_sectors
    }

    return combined



