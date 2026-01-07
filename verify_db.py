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
    with engine.connect() as conn:
        # Check one row
        df = pd.read_sql("SELECT * FROM transactions LIMIT 1", conn)
        print("Columns in DB:", df.columns.tolist())
        
        # Check count
        count = pd.read_sql("SELECT COUNT(*) as cnt FROM transactions", conn)['cnt'][0]
        print(f"Total Rows: {count}")
        
        if 'amt' in df.columns and 'tstamp_trans' in df.columns:
            print("✅ Verification Successful: New columns found.")
        else:
            print("❌ Verification Failed: New columns NOT found.")
            
except Exception as e:
    print(f"❌ Error: {e}")
