import json
from agents.agent_transaction import TransactionAgent

# DB Config
DB_CONFIG = {
    "user": "admin",
    "password": "adminpassword",
    "host": "localhost",
    "port": "5432",
    "dbname": "rupay_transactions"
}

MAPPING_FILE = "data/desc_mapping.json"

print("--- Testing TransactionAgent ---")
try:
    agent = TransactionAgent(DB_CONFIG, MAPPING_FILE)
    
    # Test Parameters (Based on sample row: 2026-01-08 22:57:33, 36545.9, card 2537)
    params = {
        "date": "2026-01-08",
        "approx_time": "22:57",
        "amount": "36545",
        "card_last_4": "2537"
    }
    
    print(f"Executing with params: {params}")
    result = agent.execute(params)
    print(result)
    
    if "No transaction found" in result:
        print("Test Failed: Transaction not found.")
    else:
        print("Test Passed: Transaction found.")

except Exception as e:
    print(f"Error: {e}")
