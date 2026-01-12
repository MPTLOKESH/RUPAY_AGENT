from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("TESTING MANDATORY PARAMETER ENFORCEMENT")
print("=" * 80)

bot = MainOrchestrator()
history = []

def test_query(test_name, query, expected_behavior_desc):
    print(f"\n[{test_name}] Query: '{query}'")
    print(f"Expected: {expected_behavior_desc}")
    print("-" * 60)
    
    response = bot.chat(query, history)
    print(f"Assistant: {response}")
    
    # Analyze if it looks like a tool call or a question
    if "provide" in response.lower() or "missing" in response.lower() or "details" in response.lower():
        print("✓ Result: Assistant asked for details (Correct for missing params)")
    elif "found a transaction" in response.lower() or "failed" in response.lower():
        print("✓ Result: Assistant tried to find transaction (Correct for full params)")
    else:
        print("? Result: Uncertain response type")
    
    # Add to history for context tests? No, keep independent for this test script usually
    # But here we want to test single turn behavior mostly.

# Test 1: Totally vague
test_query("Test 1", "My transaction failed", "Should ask for ALL details (Date, Amount, Card, Time)")

# Test 2: Partial details
test_query("Test 2", "Check my transaction of 5000 rupees", "Should ask for missing Date, Card, Time")

# Test 3: Still partial
test_query("Test 3", "Check transaction on Jan 1st for 5000", "Should ask for Card and Time")

# Test 4: Full details (using the known sample from previous tests)
# 21116 rupees on January 1, 2026 around 12:10 AM. Card ending in 8530
full_query = "Check my transaction of 21116 rupees on January 1, 2026 around 12:10 AM. Card ending in 8530."
test_query("Test 4", full_query, "Should call tool and find transaction")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
