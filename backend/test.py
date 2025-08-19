import sqlite3
import os

def test_sqlite_connection(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Successfully opened {db_path}. Tables found: {tables}")
        conn.close()
    except Exception as e:
        print(f"Error opening {db_path}: {e}")

# Print the current working directory
print("Current working directory:", os.getcwd())

# Test your agri_market.db file
test_sqlite_connection("backend/agri_market.db")