import pandas as pd

try:
    print("Inspecting data/rupay_dummy_data.xlsx...")
    df = pd.read_excel('data/rupay_dummy_data.xlsx', nrows=1)
    print(f"Columns: {df.columns.tolist()}")
    
    expected = ['amt', 'tstamp_trans', 'reason_code']
    found = [col for col in expected if col in df.columns]
    
    if len(found) == len(expected):
        print("✅ SUCCESS: Found new columns in the file.")
    else:
        print(f"❌ FAIL: Did not find all new columns. Found: {found}")
        
except Exception as e:
    print(f"Error: {e}")
