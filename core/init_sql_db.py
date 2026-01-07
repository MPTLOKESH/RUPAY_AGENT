import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION FOR DOCKER ---
DB_CONFIG = {
    "user": "admin",
    "password": "adminpassword",
    "host": "localhost",
    "port": "5432",  # <--- IMPORTANT: Using 5432 for Docker
    "dbname": "rupay_transactions" # Updated DB name
}

# Path to your RuPay data file
# Make sure to save your Excel file with this name in the 'data' folder
EXCEL_FILE = "data/rupay_dummy_data.xlsx" 

def init_db():
    print("--- Initializing Docker SQL Database for RuPay ---")
    
    # 1. Connect to SQL
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    try:
        engine = create_engine(db_url)
        conn = engine.connect()
        print(f"✅ Connected to Docker Database on Port {DB_CONFIG['port']}.")
        conn.close()
    except Exception as e:
        print(f"❌ Connection Failed. Is Docker running? Error: {e}")
        return

    # 2. Read Excel
    try:
        print(f"Reading {EXCEL_FILE}...")
        df = pd.read_excel(EXCEL_FILE)
        
        # 3. Rename columns to match SQL standards (Adapted for RuPay)
        # Actual columns found: 'rrn', 'amt', 'asdt', 'merchant_name', 'reason_code', ...
        df.rename(columns={
            "rrn": "rrn",
            "amt": "amount",
            "reason_code": "response_code",
            "reasoncodedesc": "description",
            "merchant_name": "merchant",
            "iss_bankname": "bank_name",
            "cc_dc_flag": "card_type",
            "tstamp_trans": "date_and_time"
        }, inplace=True)

        # 4. Data Type Conversion and Filling Missing Data
        import random
        
        # Generate dummy 4-digit card numbers if missing (Required for Agent lookup)
        if "card_number" not in df.columns:
            print("Generating dummy card numbers...")
            df["card_number"] = [str(random.randint(1000, 9999)) for _ in range(len(df))]
            
        # Default Transaction Type if missing
        if "transaction_type" not in df.columns:
            df["transaction_type"] = "POS Purchase"
            
        df["card_number"] = df["card_number"].astype(str)
        df["response_code"] = df["response_code"].astype(str)
        
        # Convert to datetime string format that Postgres prefers
        df["date_and_time"] = pd.to_datetime(df["date_and_time"])

        # 5. Upload to SQL
        print("Uploading data to table 'transactions'...")
        df.to_sql('transactions', engine, if_exists='replace', index=False)
        print("✅ Success! RuPay Docker Database populated.")
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")

if __name__ == "__main__":
    init_db()