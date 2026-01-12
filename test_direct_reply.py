from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("TESTING DIRECT_REPLY JSON FIX")
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

# Test 1: Missing Parameters (Should trigger direct_reply)
test_query("Test 1: Missing Params", 
           "My transaction failed.",
           "Should fallback to direct_reply -> 'Please provide details...'")

# Test 2: Incomplete details (Should trigger direct_reply)
test_query("Test 2: Still Incomplete", 
           "It was for 5000 yesterday.", 
           "Should ask for Card/Time via direct_reply.")

# Test 3: Complete details (Should trigger tool_agent)
test_query("Test 3: Complete", 
           "Card 1234, around 2 PM.", 
           "Should call tool_agent.")

# Test 4: RAG (Should work normally)
test_query("Test 4: RAG Query", 
           "What is UPI?", 
           "Should call rag_agent.")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
