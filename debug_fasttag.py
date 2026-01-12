from main_orchestraion import MainOrchestrator
import time

print("=" * 80)
print("DEBUG: TESTING 'FASTTAG' QUERY")
print("=" * 80)

bot = MainOrchestrator()
history = []

query = "fasttag"
print(f"\nQuery: '{query}'")

# We want to see the RAW output if possible, but MainOrchestrator.chat swallows it if it crashes.
# So we will access the LLM directly via the internal method if needed, 
# but first let's try the normal chat and see if it returns a 500-like message or prints the error.
try:
    response = bot.chat(query, history)
    print(f"Assistant: {response}")
except Exception as e:
    print(f"CRITICAL ERROR CAUGHT: {e}")

print("=" * 80)
