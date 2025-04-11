import sqlite3

def create_fund_table():
    connection = sqlite3.connect("fund_data.db")

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fund_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    );
    """)
    connection.commit()
    connection.close()

    print("Fund table created")

def create_holdings_table():
    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fund_holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        company_name TEXT,
        company_ticker TEXT,
        weight REAL
    );
    """)

    conn.commit()
    conn.close()

    print("Holdings table created")

def create_sectors_table():
    conn = sqlite3.connect("fund_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fund_sectors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        sector TEXT,
        weight REAL
    );
    """)

    conn.commit()
    conn.close()

    print("Sectors table created")

create_fund_table()
create_holdings_table()
create_sectors_table()
