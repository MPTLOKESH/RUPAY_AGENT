from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("TESTING STRICT SEPARATION & 38k PARSING")
print("=" * 80)

bot = MainOrchestrator()
history = []

def test_query(test_name, query, expected_behavior_desc):
    print(f"\n[{test_name}] Query: '{query}'")
    print(f"Expect: {expected_behavior_desc}")
    print("-" * 60)
    
    response = bot.chat(query, history)
    print(f"Assistant: {response}")
    
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": response})

# Test 1: "38k" Parsing
# We simulate a "complete" looking query with 38k to see if it parses
test_query("Test 1: 38k Parsing", 
           "Check txn on 2026-01-05 at 12:25 am with card 6861 for 38k.",
           "Should CALL tool with amount=38000, NOT ask for 'exact amount'.")

# Test 2: Follow-up (Context)
test_query("Test 2: Follow-up", "Why did it fail?", "Should explain using Test 1 context.")

# Test 3: New Transaction with Different Details (Mixing Check)
# User provides partial details that CONFLICT with Test 1 (Card 1234 instead of 6861)
# Assistant must NOT use Date/Time from Test 1.
test_query("Test 3: New Txn, New Card", 
           "My card ending 1234 failed.", 
           "Should ask for Date/Time/Amount. MUST NOT use Jan 5 or 38k.")

# Test 4: "Another failed" (Ambiguous)
test_query("Test 4: Another Failed", 
           "I have another failed transaction.", 
           "Should ask for ALL details. MUST NOT assume anything.")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
