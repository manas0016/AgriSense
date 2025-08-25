import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlencode
import time
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
# agrimarket/CommodityAndCommodityHeads.csv
load_dotenv()
# Load commodity codes
if not os.path.exists('CommodityAndCommodityHeads.csv'):
    raise FileNotFoundError("CommodityAndCommodityHeads.csv not found in agrimarket directory.")
commodities = pd.read_csv('CommodityAndCommodityHeads.csv')


def get_url(Commodity, CommodityHead, Market=0, date_from=None, date_to=None):
    base_url = 'https://agmarknet.gov.in/SearchCmmMkt.aspx'
    if date_to is None:
        date_to = datetime.today()
    if date_from is None:
        date_from = date_to
    date_from_str = date_from.strftime('%d-%b-%Y')
    date_to_str = date_to.strftime('%d-%b-%Y')
    parameters = {
        "Tx_Commodity": Commodity,
        "Tx_State": "0",
        "Tx_District": 0,
        "Tx_Market": 0,  # All markets
        "DateFrom": date_from_str,
        "DateTo": date_to_str,
        "Fr_Date": date_from_str,
        "To_Date": date_to_str,
        "Tx_Trend": 0,
        "Tx_CommodityHead": CommodityHead,
        "Tx_StateHead": "--Select--",
        "Tx_DistrictHead": "--Select--",
        "Tx_MarketHead": "--Select--",
    }
    query = urlencode(parameters)
    return f"{base_url}?{query}"


def get_soup_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return bs(response.text, "html.parser")


def get_all_tables(soup):
    return soup.find_all("table")


def get_table_headers(table):
    headers = []
    for th in table.find("tr").find_all("th"):
        headers.append(th.text.strip())
    return headers


def get_table_rows(table):
    rows = []
    for tr in table.find_all("tr")[1:]:
        cells = []
        tds = tr.find_all("td")
        for td in tds:
            cells.append(td.text.strip())
        rows.append(cells)
    return rows


def daily_update(num_days=45):
    # Connect to SQLite database
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set in .env file.")
        return
    engine = create_engine(db_url)
    # Load existing data from DB
    try:
        df = pd.read_sql_table('market_prices', engine)
    except Exception:
        print("Table does not exist. Creating new table.")
        df = pd.DataFrame()
    # Find the date column
    date_col = None
    if not df.empty:
        date_col = [col for col in df.columns if 'Date' in col or 'date' in col][0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    else:
        # Guess the column name for new data
        date_col = 'Price Date'

    # Calculate the date range for the latest num_days
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    date_list = [(today - timedelta(days=i)).date() for i in range(num_days-1, -1, -1)]

    # Find which dates are missing in the DB
    existing_dates = set()
    if not df.empty:
        existing_dates = set(df[date_col].dt.date.unique())
    missing_dates = [d for d in date_list if d not in existing_dates]

    # Scrape and insert missing dates
    from sqlalchemy import text
    for target_date in missing_dates:
        print(f"Fetching data for missing date: {target_date}")
        all_data = []
        for _, commodity in commodities.iterrows():
            commodity_code = commodity['Commodity']
            commodity_head = commodity['CommodityHead']
            url = get_url(commodity_code, commodity_head, Market=0, date_from=target_date, date_to=target_date)
            print(f"  Commodity {commodity_code} - {commodity_head}")
            try:
                soup = get_soup_from_url(url)
                tables = get_all_tables(soup)
                if not tables:
                    continue
                table = tables[0]
                headers = get_table_headers(table)
                rows = get_table_rows(table)
                for row in rows:
                    if len(row) == len(headers):
                        all_data.append(dict(zip(headers, row)))
                time.sleep(1)
            except Exception as e:
                print(f"Error fetching all markets - {commodity_code}: {e}")
        if all_data:
            new_df = pd.DataFrame(all_data)
            new_df.to_sql('market_prices', engine, if_exists='append', index=False)
            print(f"Appended {len(new_df)} new rows for {target_date} to the database.")
        else:
            print(f"No new data scraped for {target_date}.")

    # Delete data older than the window
    min_date = date_list[0]
    with engine.begin() as conn:
        conn.execute(
            text(f'DELETE FROM market_prices WHERE \"{date_col}\" < :min_date'),
            {"min_date": min_date.strftime('%Y-%m-%d')}
        )
    print(f"Deleted data older than {min_date}.")

if __name__ == "__main__":
    daily_update(num_days=45)
