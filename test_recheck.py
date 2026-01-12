from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("TESTING RE-CHECK vs NEW vs FOLLOW-UP")
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

# Test 1: Initial Query
test_query("Test 1: Initial", 
           "Check txn on 2026-01-05 at 12:25 am with card 6861 for 38k.",
           "Confirm & Call Tool")

# Test 2: Standard Follow-up
test_query("Test 2: Follow-up", "Why did it fail?", "Explain using context (No tool call needed usually, or same tool call)")

# Test 3: Re-check (Explicit)
test_query("Test 3: Re-check", "Check that transaction again.", "Call Tool using SAME parameters from Test 1")

# Test 4: New Transaction (Ambiguous)
test_query("Test 4: New Txn", "Transaction failed.", "Ask for NEW details (Date/Amount/etc.). Do NOT use Test 1 data.")

# Test 5: New Transaction (Explicit Conflict)
test_query("Test 5: Explicit New", "Check for card 1234.", "Ask for details for card 1234. Do NOT use Test 1 Date.")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
