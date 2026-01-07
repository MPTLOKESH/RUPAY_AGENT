import pandas as pd

try:
    df = pd.read_excel(r'c:\Users\admin\Downloads\llm_code_rupay\llm_code\llm_code\data\rupay_dummy_data_final_v2.xlsx')
    print("Columns:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())
except Exception as e:
    print(f"Error reading excel: {e}")
