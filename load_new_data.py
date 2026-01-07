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
    print("Reading Excel file...")
    # Load available Excel file
    df = pd.read_excel('data/rupay_dummy_data.xlsx')
    
    print(f"Loaded {len(df)} rows. Columns: {df.columns.tolist()}")

    # Pre-processing
    if 'card_number' in df.columns:
        df['card_number'] = df['card_number'].astype(str)
    
    if 'tstamp_trans' in df.columns:
        df['tstamp_trans'] = pd.to_datetime(df['tstamp_trans'])
    elif 'date_and_time' in df.columns:
        df['date_and_time'] = pd.to_datetime(df['date_and_time'])

    print("Connecting to Database...")
    engine = create_engine(db_url)
    
    print("Replacing 'transactions' table...")
    df.to_sql('transactions', engine, if_exists='replace', index=False)
    
    print("Database updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
