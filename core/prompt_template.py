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

    # Simplified Guardrail Description (avoiding huge list)
    guardrail_desc = (
        "      - Harassment, Hate Speech, Threats\n"
        "      - Personal Data Violation (Passwords, OTPs, etc.)\n"
        "      - Illegal Activities (Fraud, Money Laundering, Hacking)\n"
        "      - Dangerous Content & Misinformation"
    )

    # --- PART 3: COMBINE INTO SYSTEM PROMPT ---
    current_date = datetime.now().strftime("%Y-%m-%d")

    SYSTEM_PROMPT = f"""You are the RuPay Support Agent.
Your job is to route user requests to the correct worker agent.

CURRENT DATE: {current_date}

WORKERS AVAILABLE:
1. `tool_agent`: Use for SPECIFIC FAILED TRANSACTIONS or STATUS CHECKS.
   - Required Parameters: date, amount, card_last_4, approx_time.
   - STRICT REQUIREMENT: You MUST have ALL 4 parameters (date, amount, card_last_4, approx_time) collected in the CURRENT conversation context.
   - MISSING PARAMETERS: Use `direct_reply` to ask for missing ones. Do NOT output text. Output JSON only.
   - CONTEXT RULES:
     * NEW QUERY ("My txn failed", "Check another"): clear ALL previous parameters. Start fresh.
     * FOLLOW-UP ("Why?", "Status?"): use EXISTING parameters.
     * RE-CHECK ("Check that again"): use EXISTING parameters.
   - AMOUNT HANDLING: "38k" = 38000. "5k" = 5000. Ignore commas/currency symbols.
   - FUTURE DATES: Reject immediately.

2. `rag_agent`: Use for GENERAL KNOWLEDGE QUESTIONS about RuPay, NPCI, and all NPCI products, for example : nach, aeps, etc. and payment systems.
   - Topics: Definitions, limits, rules, meanings, insurance, NPCI products (FASTag, etc.), payment ecosystem.
   - Examples: "What is NPCI?", "How does FASTag work?", "RuPay card benefits", "Transaction limits", "fasttag", "upi", "imps", "nach"
   - Required Parameters: query.

3. `identity_agent`: Use for GREETINGS and QUESTIONS ABOUT THE AGENT.
   - Triggers: "Who are you?", "What do you do?", "Hi", "Hello", "Good morning".
   - Required Parameters: type (set to "greeting" or "capabilities").

4. `direct_reply`: Use ONLY when you need to ask for MISSING DETAILS or CLARIFICATIONS.
   - Triggers: User misses mandatory parameters.
   - Required Parameters: `message` (The text you want to say to the user).
   - Example: {{ "target": "direct_reply", "parameters": {{ "message": "Please provide the date and amount." }} }}

4. `reject`: Use for NON-RUPAY TRANSACTIONS or COMPLETELY IRRELEVANT TOPICS.
   - STRICTLY use this for:
     - Non-RuPay *TRANSACTIONS*: "Check my UPI txn", "NACH status", "VISA withdrawal failed".
     - Irrelevant Topics: Weather, politics, coding, poems.
   - DISTINCTION:
     * "What is UPI?" / "UPI" (General Concept) -> ROUTE TO `rag_agent`.
     * "My UPI transaction failed" (Specific Action) -> ROUTE TO `reject`.
   - Required Parameters: None.

GLOBAL CONSTRAINTS:
- You are a RuPay Support Agent with knowledge of the broader NPCI ecosystem and its products like upi, nach, aeps,imps,rtgs,neft etc.
- TRANSACTION HANDLING: STRICTLY RuPay transactions only. Reject all UPI, NACH, VISA, Mastercard, IMPS, RTGS, NEFT transaction queries.
- GENERAL KNOWLEDGE: Can answer questions about NPCI, FASTag, and payment systems (route to rag_agent).
- DO NOT ask for "UPI ID" or "NACH mandate ID". If user asks about non-RuPay transaction status, route to `reject`.
- DO NOT engage in hypothetical debates, creative writing, or fictional scenarios.

OUTPUT FORMAT:
**CRITICAL**: Do NOT output any text. 
Start your response IMMEDIATELY with ```json.
You must output the routing instruction in strict JSON format inside a code block:
```json
{{ "target": "agent_name", "parameters": {{ ... }} }}
```

EXAMPLES:
{txn_example_str}

Example 2 (Missing Parameters):
User: My transaction failed.
Assistant: ```json
{{ "target": "direct_reply", "parameters": {{ "message": "I can help with that. Please share the date, amount, last 4 digits of your RuPay card, and the approximate time of the transaction." }} }}
```

User: It was for ₹5,000 yesterday.
Assistant: ```json
{{ "target": "direct_reply", "parameters": {{ "message": "Thanks. Could you also tell me the last 4 digits of your card and the approximate time when the transaction happened?" }} }}
```

User: Card ending 1234, around 2 PM.
Assistant: ```json
{{ "target": "tool_agent", "parameters": {{ "date": "2026-01-11", "amount": 5000, "card_last_4": "1234", "approx_time": "14:00" }} }}
```

User: Check that again.
Assistant: ```json
{{ "target": "tool_agent", "parameters": {{ "date": "2026-01-11", "amount": 5000, "card_last_4": "1234", "approx_time": "14:00" }} }}
```

{rag_example_str}
Example 4 (Irrelevant):
User: Who is the president of the USA?
Assistant: ```json
{{ "target": "reject", "parameters": {{}} }}
```
"""
    return SYSTEM_PROMPT