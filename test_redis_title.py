
from core.redis_client import save_title, get_title
import time

def test_title_persistence():
    session_id = f"test_session_{int(time.time())}"
    title = "Test Chat Title"
    
    print(f"Testing with Session ID: {session_id}")
    
    # Test 1: Save Title
    print("Saving title...")
    save_title(session_id, title)
    
    # Test 2: Get Title
    print("Retrieving title...")
    retrieved_title = get_title(session_id)
    
    if retrieved_title == title:
        print("✅ SUCCESS: Title retrieved correctly.")
    else:
        print(f"❌ FAILURE: Expected '{title}', got '{retrieved_title}'")

if __name__ == "__main__":
    test_title_persistence()
