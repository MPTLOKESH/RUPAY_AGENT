from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("TESTING STRICT TRANSACTION PARAMETERS & HALLUCINATION PREVENTION")
print("=" * 80)

bot = MainOrchestrator()
history = []

def test_query(test_name, query, expected_behavior_desc):
    print(f"\n[{test_name}] Query: '{query}'")
    print(f"Expect: {expected_behavior_desc}")
    print("-" * 60)
    
    # We append previous interactions to history to simulate a continuous session
    response = bot.chat(query, history)
    print(f"Assistant: {response}")
    
    # Simulate history update (simplified for test script)
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": response})

# Test 1: Incomplete Query (Should ask for details, NOT call tool)
test_query("Test 1: Incomplete", "My transaction failed.", "Ask for Date, Amount, Card, Time")

# Test 2: Another Incomplete Query (Should NOT use previous contex to guess)
test_query("Test 2: Another Incomplete", "Another transaction failed yesterday.", "Ask for Date, Amount, Card, Time (fresh)")

# Test 3: Complete Query (Should call tool)
# Using a valid date for "future check" bypass - assume today is handled or used past date
# 2024-01-01 is safe past date
test_query("Test 3: Complete", "Check transaction on 2024-01-01 for 5000 rupees, card 1234, at 10 AM.", "Call tool_agent")

# Test 4: Follow up on Test 3 (Should NOT re-confirm)
test_query("Test 4: Follow-up", "Why did it fail?", "Explain failure using context")

# Test 5: New Transaction Failure (Should NOT use Test 3's data)
test_query("Test 5: New Failure", "I have another failed transaction.", "Ask for NEW details. Do NOT assume card 1234.")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
