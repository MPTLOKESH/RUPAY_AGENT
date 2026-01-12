from agents.agent_transaction import TransactionAgent
from core.prompt_template import get_orchestrator_prompt
import json

# DB Config (Mock or Real)
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "admin",
    "password": "adminpassword",
    "dbname": "rupay_transactions"
}
MAPPING_FILE = "data/desc_mapping.json"

def test_future_date():
    print("Testing Future Date Validation...")
    agent = TransactionAgent(DB_CONFIG, MAPPING_FILE)
    
    # Test Case: Future Date
    params = {
        "date": "2030-01-01",
        "approx_time": "10:00",
        "amount": 5000,
        "card_last_4": "1234"
    }
    
    result = agent.execute(params)
    print(f"Result: {result}")
    
    if "Invalid Date (Future)" in result:
        print("SUCCESS: Future date was rejected.")
    else:
        print("FAILURE: Future date was NOT rejected.")

if __name__ == "__main__":
    test_future_date()
