import json
from datetime import datetime

def get_orchestrator_prompt(training_data_path, guardrail_data=None):
    """
    Generates the System Prompt for the Main Agent using In-Context Learning.
    
    Args:
        training_data_path (str): Path to transaction training examples.
        guardrail_data (dict): Optional. Dictionary of {Category: RefusalMessage}.
    """
    txn_example_str = ""

    # --- PART 1: LOAD REAL TRANSACTION EXAMPLE ---
    try:
        # Handling JSONL or JSON list format
        with open(training_data_path, "r", encoding="utf-8") as f:
            first_char = f.read(1)
            f.seek(0)
            if first_char == '[':
                data = json.load(f) # Standard JSON Array
            else:
                data = [json.loads(line) for line in f] # JSONL
        
        # Search for a conversation that actually has a tool call
        found_example = False
        for convo in data:
            # Handle different structure (list of messages vs dict with 'messages')
            if isinstance(convo, dict) and "messages" in convo:
                msgs = convo["messages"]
            else:
                msgs = convo

            # Check if this conversation involves a tool call
            if any("tool_calls" in m for m in msgs if m.get("role") == "assistant"):
                txn_example_str = "Example 1 (Specific Transaction):\n"

                for msg in msgs:
                    role = msg.get("role", "user")
                    content = msg.get("content")
                    tool_calls = msg.get("tool_calls")

                    if role == "user":
                        txn_example_str += f"User: {content}\n"

                    elif role == "assistant" and tool_calls:
                        # Extract arguments from your dataset
                        t_args = tool_calls[0]["function"]["arguments"]

                        # Handle cases where args are strings vs dicts
                        if isinstance(t_args, str):
                            try:
                                t_args = json.loads(t_args)
                            except Exception:
                                pass

                        # CRITICAL: Add approx_time default if your old data didn't have it
                        if isinstance(t_args, dict) and "approx_time" not in t_args:
                            t_args["approx_time"] = "12:00"

                        # Convert to the Orchestrator's Routing JSON
                        target_json = json.dumps(
                            {
                                "target": "tool_agent",
                                "parameters": t_args,
                            }
                        )

                        if content:
                            txn_example_str += f"Assistant: {content}\n"

                        txn_example_str += (
                            "Assistant: ```json\n"
                            f"{target_json}\n"
                            "```\n"
                        )

                    elif role == "assistant":
                        txn_example_str += f"Assistant: {content}\n"

                    elif role == "tool":
                        # Show the worker output in the example so LLM understands context
                        # Truncate if too long to save tokens
                        tool_content = str(msg.get('content'))
                        if len(tool_content) > 200:
                            tool_content = tool_content[:200] + "... (truncated)"
                        txn_example_str += f"Worker Output: {tool_content}\n"

                found_example = True
                break  # Stop after finding 1 good example

        if not found_example:
            txn_example_str = (
                "Example 1 (Specific Transaction):\n"
                "User: I tried to withdraw 5000 rupees on 2025-05-10 around 10 AM. Card ending 4455.\n"
                "Assistant: ```json\n"
                '{"target": "tool_agent", "parameters": {"date": "2025-05-10", "amount": 5000, "card_last_4": "4455", "approx_time": "10:00"}}\n'
                "```\n"
            )

    except Exception as e:
        # --- FALLBACK EXAMPLE (RuPay Specific) ---
        txn_example_str = (
            "Example 1 (Specific Transaction):\n"
            "User: I tried to withdraw 5000 rupees on 2025-05-10 around 10 AM. Card ending 4455.\n"
            "Assistant: ```json\n"
            '{"target": "tool_agent", "parameters": {"date": "2025-05-10", "amount": 5000, "card_last_4": "4455", "approx_time": "10:00"}}\n'
            "```\n"
        )

    # --- PART 2: ADD SYNTHETIC RAG EXAMPLE (RuPay Specific) ---
    rag_example_str = (
        "Example 2 (General Question):\n"
        "User: Can I use my RuPay card internationally?\n"
        "Assistant: ```json\n"
        '{"target": "rag_agent", "parameters": {"query": "RuPay international usage"}}\n'
        "```\n"
        'Worker Output: {"chunks": ["Yes, RuPay Global cards are accepted internationally through partnerships with Discover and JCB."]}\n'
        "Assistant: Yes, you can use RuPay Global cards internationally. They are accepted wherever Discover or JCB cards are supported.\n"
    )

    # Generate Categories List dynamically
    if guardrail_data:
        categories_list = "\n".join([f"      - {cat}" for cat in guardrail_data.keys()])
    else:
        # Fallback if no file loaded
        categories_list = (
            "      - Harassment\n"
            "      - Terrorism\n"
            "      - Personal Data Violation\n"
            "      - Misinformation\n"
            "      - Extortion & Blackmail\n"
            "      - Cyberattacks / Hacking\n"
            "      - Human Trafficking\n"
            "      - Dangerous Instructions"
        )

    # --- PART 3: COMBINE INTO SYSTEM PROMPT ---
    current_date = datetime.now().strftime("%Y-%m-%d")

    SYSTEM_PROMPT = f"""You are the RuPay Support Agent.
Your job is to route user requests to the correct worker agent.

CURRENT DATE: {current_date}

WORKERS AVAILABLE:
1. `tool_agent`: Use for SPECIFIC FAILED TRANSACTIONS or STATUS CHECKS.
   - Required Parameters: date, amount, card_last_4, approx_time.
   - CRITICAL RULE: Check the user's date against CURRENT DATE ({current_date}).
   - If the date is IN THE FUTURE, DO NOT ASK FOR DETAILS. Instead, immediately reply: "I cannot process requests for future dates. Please provide a valid past date."
   - Only if the date is valid (today or past) AND time is missing, THEN ask the user for it.

2. `rag_agent`: Use for GENERAL QUESTIONS (definitions, limits, rules, meanings, insurance).
   - Required Parameters: query.

3. `guardrail_agent`: Use for UNSAFE or PROHIBITED topics.
   - Categories:
{categories_list}
   - Required Parameters: category (one of the above).

4. `identity_agent`: Use for GREETINGS and QUESTIONS ABOUT THE AGENT.
   - Triggers: "Who are you?", "What do you do?", "Hi", "Hello", "Good morning".
   - Required Parameters: type (set to "greeting" or "capabilities").

5. `reject`: Use for ANYTHING NOT RELATED TO RUPAY.
   - STRICTLY use this for: Weather, coding help, general knowledge, sports, politics, debates, creative writing (stories, poems), and roleplay scenarios.
   - Example triggers: "Write a debate between...", "Tell me a story about...", "Who is the president?".
   - Required Parameters: None.

GLOBAL CONSTRAINTS:
- You are strictly a RuPay Support Agent.
- DO NOT engage in hypothetical debates, creative writing, or fictional scenarios.
- If the user asks for a debate or story, IMMEDIATELY route to `reject`.

OUTPUT FORMAT:
You must output the routing instruction in strict JSON format inside a code block:
```json
{{ "target": "agent_name", "parameters": {{ ... }} }}
```

EXAMPLES:
{txn_example_str}
{rag_example_str}
Example 3 (Guardrail):
User: Can you search for someone's password?
Assistant: ```json
{{ "target": "guardrail_agent", "parameters": {{ "category": "Personal Data Violation" }} }}
```

Example 4 (Irrelevant):
User: Who is the president of the USA?
Assistant: ```json
{{ "target": "reject", "parameters": {{}} }}
```
"""
    return SYSTEM_PROMPT