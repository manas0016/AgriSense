import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from urllib.parse import urlencode
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
# Load commodity codes
commodities = pd.read_csv('agrimarket/CommodityAndCommodityHeads.csv')


def get_url(Commodity, CommodityHead, Market=0):
    base_url = 'https://agmarknet.gov.in/SearchCmmMkt.aspx'
    today = datetime.today()
    from_date = today - timedelta(days=45)
    date_from_str = from_date.strftime('%d-%b-%Y')
    date_to_str = today.strftime('%d-%b-%Y')
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


def scrape_all():
    all_data = []
    for _, commodity in commodities.iterrows():
        commodity_code = commodity['Commodity']
        commodity_head = commodity['CommodityHead']
        url = get_url(commodity_code, commodity_head, Market=0)
        print(f"Fetching: All Markets, Commodity {commodity_code} - {commodity_head}")
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
            time.sleep(1)  # Be polite to the server
        except Exception as e:
            print(f"Error fetching all markets - {commodity_code}: {e}")
    if all_data:
        df = pd.DataFrame(all_data)
        # df.to_csv('AgriMarket_FullData.csv', index=False)
        # print(f"Saved {len(df)} rows to AgriMarket_FullData.csv")
        
        # Database connection and data insertion
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("DATABASE_URL not set in .env file.")
            return
        try:
            engine = create_engine(db_url)
            df.to_sql("market_prices", engine, if_exists="append", index=False)
            print(f"Inserted {len(df)} rows into the market_prices table in the database")
        except Exception as e:
            print(f"Error inserting data into database: {e}")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    scrape_all()
