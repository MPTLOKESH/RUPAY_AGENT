import pandas as pd
from sqlalchemy import create_engine

# DB Config
DB_CONFIG = {
    "user": "admin",
    "password": "adminpassword",
    "host": "localhost",
    "port": "5432",
    "dbname": "rupay_transactions"
}

db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

try:
    engine = create_engine(db_url)
    # Search for any transaction with this card suffix
    query = "SELECT * FROM transactions WHERE card_number LIKE '%%2583'"
    df = pd.read_sql(query, engine)
    
    print(f"Found {len(df)} transactions for card *2583:")
    print(df.to_string())
except Exception as e:
    print(f"Error querying DB: {e}")
