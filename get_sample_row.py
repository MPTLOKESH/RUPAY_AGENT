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
    # Fetch one row
    df = pd.read_sql("SELECT * FROM transactions LIMIT 1", engine)
    print("SAMPLE ROW:")
    print(df.iloc[0].to_dict())
except Exception as e:
    print(f"Error: {e}")
