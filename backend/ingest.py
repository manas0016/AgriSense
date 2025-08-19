import os
from main import (
    ingest_state_txts,
    ingest_all_csvs,
    ingest_pdfs,
    ingest_seed_csvs,
    ingest_sqlite_db
)

# Path to the SQLite DB in the same directory
db_file_path = os.path.join(os.path.dirname(__file__), "agri_market.db")

# Run ingestion steps
ingest_state_txts()
ingest_all_csvs()
ingest_pdfs()
ingest_seed_csvs()
ingest_sqlite_db(db_file_path, "market_prices", chunk_size=500)  # Larger chunk size for performance
