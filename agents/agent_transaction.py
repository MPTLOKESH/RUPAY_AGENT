import json
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dateutil import parser  # Required for smart time parsing

class TransactionAgent:
    def __init__(self, db_config, mapping_path):
        """
        db_config: Dictionary containing host, user, password, db_name
        mapping_path: Path to the JSON file with response code descriptions
        """
        print(f"[TxAgent] Connecting to SQL Database...")
        try:
            # --- 1. Connect to Docker Database ---
            db_url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
            self.engine = create_engine(db_url)
            
            # Test connection
            with self.engine.connect() as conn:
                print("[TxAgent] DB Connection Successful.")

            # --- 2. Load Mapping JSON ---
            with open(mapping_path, "r", encoding="utf-8") as f:
                self.codes = json.load(f)
                
        except Exception as e:
            print(f"[TxAgent] Error connecting to DB or loading files: {e}")
            self.engine = None
            self.codes = []



    def execute(self, params):
        date = params.get("date")
        approx_time = params.get("approx_time")
        amount = params.get("amount")
        card_last_4 = params.get("card_last_4")

        # --- Logic: Mandatory Check ---
        if not approx_time or str(approx_time).lower() in ["none", "null", ""]:
             return json.dumps({"status": "Error", "message": "Time is mandatory. Ask user for approx_time."})

        if not self.engine:
            return json.dumps({"status": "Error", "message": "Database not connected."})

        try:
            # --- Logic: Smart Date Parsing (Handles '12.30', '12:30 am', etc.) ---
            # We combine date + time and let dateutil figure out the format
            dt_str = f"{date} {approx_time}"
            try:
                # dayfirst=False ensures YYYY-MM-DD is respected
                user_dt = parser.parse(dt_str, dayfirst=False) 
            except:
                # Fallback if parser fails
                user_dt = datetime.strptime(f"{date} {approx_time}", "%Y-%m-%d %H:%M")

            # Define initial window (+/- 1 Hour)
            start_dt = user_dt - timedelta(hours=1)
            end_dt = user_dt + timedelta(hours=1)

            # --- Logic: Calculate Amount Window (Broad Match) ---
            # User might say "around 33000" for a 33851 txn.
            # We allow +/- 20% tolerance.
            amt_val = float(amount)
            min_amount = amt_val * 0.8  # -20%
            max_amount = amt_val * 1.2  # +20%

            # --- Logic: SQL Query Template ---
            # NOTE: Using 'transactions' table with NEW columns
            query_str = """
                SELECT * FROM transactions 
                WHERE amt BETWEEN :min_amt AND :max_amt
                AND card_number LIKE :card_pattern
                AND tstamp_trans BETWEEN :start_dt AND :end_dt
                ORDER BY tstamp_trans DESC
                LIMIT 1
            """
            
            common_params = {
                "min_amt": min_amount,
                "max_amt": max_amount,
                "card_pattern": f"%{card_last_4}",
            }

            row = None
            with self.engine.connect() as conn:
                # --- Attempt 1: Specific Window (+/- 2 Hours) ---
                start_window = user_dt - timedelta(hours=2)
                end_window = user_dt + timedelta(hours=2)
                
                params1 = {**common_params, "start_dt": start_window, "end_dt": end_window}
                result = conn.execute(text(query_str), params1)
                row = result.fetchone()

                # --- Attempt 2: Whole Day Fallback ---
                if not row:
                    print(f"[TxAgent] Specific window {start_window}-{end_window} failed. Trying Whole Day...")
                    day_start = user_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    day_end = user_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
                    
                    params2 = {**common_params, "start_dt": day_start, "end_dt": day_end}
                    result = conn.execute(text(query_str), params2)
                    row = result.fetchone()

                # --- Attempt 3: +/- 12 Hours Flip (Legacy Logic) ---
                if not row:
                    alt_start = start_window + timedelta(hours=12)
                    alt_end = end_window + timedelta(hours=12)
                    
                    params3 = {**common_params, "start_dt": alt_start, "end_dt": alt_end}
                    result = conn.execute(text(query_str), params3)
                    row = result.fetchone()

            # --- Logic: Return Results ---
            if not row:
                return json.dumps({"response_code": "91", "description": "No transaction found."})

            # Get Description and Agent Message
            # Mapped response_code -> reason_code (new column)
            details = self._get_details(row.reason_code)

            return json.dumps({
                "date": str(row.tstamp_trans),
                "amount": f"{int(row.amt):,}", # formatted as string with commas (e.g., "43,402")
                "status": "Failed" if row.reason_code != "00" else "Success",
                "reason_code": str(row.reason_code),
                "error_reason": details["description"],
                "suggested_message": details["agent_message"]
            })

        except Exception as e:
            return json.dumps({"status": "Error", "message": f"DB Error: {str(e)}"})
            
    def _get_details(self, resp_code):
        """Helper to find details from loaded JSON mapping"""
        for item in self.codes:
            tech = item.get("technical_details", {})
            if str(tech.get("Resp Code")) == str(resp_code):
                return {
                    "description": tech.get("Response Desc", "UNKNOWN"),
                    "agent_message": item.get("agent_message", "Transaction failed.")
                }
        return {"description": "UNKNOWN RESPONSE CODE", "agent_message": "Transaction failed with unknown error."}