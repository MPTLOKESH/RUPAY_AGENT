import sys
import os

# Add current directory to path so it behaves like running from root
sys.path.append(os.getcwd())

try:
    from core.rag_pipeline import RupayRAG
    print("Import successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
