import requests
import json
import random
import uuid
import string
import math
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
API_URL = "http://183.82.7.228:9532/v1/chat/completions"
API_KEY = "EMPTY"
TARGET_COUNT = 10  # Total conversations to generate

# ================= 1. DATA SOURCES (RUPAY SPECIFIC) =================

# Based on Standard RuPay/ISO 8583 Response Codes
SCENARIOS = [
    {
        "code": "00",
        "desc": "Transaction Successful",
        "agent_msg": "Your transaction was successful."
    },
    {
        "code": "51",
        "desc": "Insufficient Funds",
        "agent_msg": "The transaction was declined due to insufficient funds in your account. Please check your balance."
    },
    {
        "code": "55",
        "desc": "Incorrect PIN",
        "agent_msg": "The PIN entered is incorrect. Please retry with the correct PIN. Note that 3 wrong attempts will block your card."
    },
    {
        "code": "61",
        "desc": "Exceeds Withdrawal Amount Limit",
        "agent_msg": "This amount exceeds the withdrawal limit defined for your card type. Please try a smaller amount."
    },
    {
        "code": "91",
        "desc": "Issuer Switch Inoperative",
        "agent_msg": "Your bank's system is currently down (Issuer Switch Inoperative). Please try the transaction again later."
    },
    {
        "code": "41",
        "desc": "Lost Card",
        "agent_msg": "This card has been reported as lost. The transaction is declined, and the card should be retained."
    },
    {
        "code": "54",
        "desc": "Expired Card",
        "agent_msg": "Your RuPay card has expired. Please contact your branch to get a new card issued."
    },
    {
        "code": "45",
        "desc": "Function Not Supported",
        "agent_msg": "This specific transaction type is not supported for your card (e.g., International usage disabled)."
    },
    {
        "code": "05",
        "desc": "Do Not Honor",
        "agent_msg": "The bank has declined this transaction without a specific reason (Do Not Honor). Please contact your branch."
    },
    {
        "code": "U6",
        "desc": "App/Daily Limit Exceeded",
        "agent_msg": "You have exceeded your daily transaction count or value limit set by the bank."
    },
    {
        "code": "96",
        "desc": "System Malfunction",
        "agent_msg": "There was a technical system malfunction during processing. Please try again."
    }
]

# Based on the RuPay FAQs provided
RAG_TOPICS = [
    {
        "query": "What is RuPay?",
        "context": "RuPay is a domestic card payment network developed by NPCI. The name is a blend of 'Rupee' and 'Payment'. It aims to create a cashless economy and financial inclusion in India.",
        "intent": "Definition"
    },
    {
        "query": "Can I use RuPay cards internationally?",
        "context": "Yes, RuPay Global cards are accepted internationally through partnerships with Discover Financial Services (USA) and JCB (Japan).",
        "intent": "International Usage"
    },
    {
        "query": "What is the limit for contactless transactions without PIN?",
        "context": "For RuPay Contactless cards, transactions up to ₹5,000 do not require a PIN. You can simply tap to pay. Amounts above ₹5,000 require a PIN.",
        "intent": "Contactless Limits"
    },
    {
        "query": "Does RuPay provide insurance?",
        "context": "Yes, many RuPay cards (like PMJDY, Platinum, and Select) come with complimentary Personal Accident Insurance (Death and Permanent Total Disability). The coverage amount depends on the card variant.",
        "intent": "Insurance"
    },
    {
        "query": "What is the 'RuPay - Tokenization' feature?",
        "context": "Tokenization allows you to replace sensitive card details with a unique 'Token'. This enables secure payments on smartphones or IoT devices without sharing actual card numbers.",
        "intent": "Security"
    },
    {
        "query": "Who developed RuPay?",
        "context": "RuPay was developed by the National Payments Corporation of India (NPCI) to fulfill the RBI's vision of a domestic, open-loop payment system.",
        "intent": "Origin"
    },
    {
        "query": "What are the different types of RuPay cards?",
        "context": "RuPay offers Credit, Debit, and Prepaid cards. Variants include Government schemes (PMJDY, MUDRA, Kisan), Classic, Platinum, Select, and RuPay Ekaa for high net-worth individuals.",
        "intent": "Card Types"
    },
    {
        "query": "How do I get a RuPay card?",
        "context": "You can get a RuPay card by opening a bank account with any participating bank in India. You can specifically request a RuPay Debit or Credit card from your branch.",
        "intent": "Acquisition"
    },
    {
        "query": "Is my RuPay card secure?",
        "context": "Yes, RuPay cards use EMV Chip technology for skimming protection, 2-Factor Authentication (PIN/OTP) for online transactions, and Tokenization for device payments.",
        "intent": "Security"
    },
    {
        "query": "Can I use RuPay for online shopping?",
        "context": "Yes, RuPay cards are accepted on almost all domestic e-commerce websites and payment gateways. You will need your card details and an OTP for authentication.",
        "intent": "Usage"
    }
]

PERSONAS = [
    "A senior citizen (struggling with ATM technology, worried about pension)",
    "A college student (trying to pay fees online, tech-savvy but impatient)",
    "A small shopkeeper (trying to withdraw cash for inventory, pragmatic)",
    "A first-time card user (confused about PIN vs OTP, hesitant)",
    "A traveling professional (trying to use card at an airport, urgent)",
    "A rural farmer (beneficiary of Kisan Credit Card, speaks simple language)",
    "A gig worker (delivery partner, needs cash for fuel immediately)",
    "A skeptical user (worried about fraud, asks many security questions)",
    "An angry customer (transaction failed but money deducted, demanding refund)",
    "A curious user (asking about benefits like insurance or lounge access)"
]

BANK_LIST = ['State Bank of India', 'HDFC Bank', 'ICICI Bank', 'Punjab National Bank', 'Bank of Baroda', 'Union Bank']

# ================= UTILS =================
def generate_dates():
    start_date = datetime(2025, 1, 1)
    txn_dt = start_date + timedelta(days=random.randint(0, 300))
    txn_dt = txn_dt.replace(hour=random.randint(8, 20), minute=random.randint(0, 59))
    
    if random.random() < 0.8:
        curr_dt = txn_dt + timedelta(minutes=random.randint(2, 60))
        note = "Reporting immediately."
    else:
        curr_dt = txn_dt + timedelta(days=random.randint(1, 3))
        note = "Reporting past transaction."

    return {
        "txn_date": txn_dt.strftime("%Y-%m-%d"),
        "txn_time": txn_dt.strftime("%H:%M"),
        "txn_full": txn_dt.strftime("%Y-%m-%d %H:%M:00"),
        "curr_date": curr_dt.strftime("%Y-%m-%d"),
        "curr_time": curr_dt.strftime("%H:%M:%S"),
        "note": note
    }

# ================= PROMPT 1: TRANSACTION (TOOL CALL) =================
def get_transaction_prompt(scenario, persona):
    d = generate_dates()
    rand_amt = random.randint(500, 10000)
    rand_last4 = str(random.randint(1000, 9999))
    merchant = random.choice(["Amazon", "Flipkart", "Local ATM", "Petrol Pump", "Grocery Store"])
    call_id = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    rrn = ''.join([str(random.randint(0, 9)) for _ in range(12)])

    tool_output = json.dumps({
        "rrn": rrn,
        "amount": rand_amt,
        "merchant_or_atm": merchant,
        "datetime": d['txn_full'],
        "response_code": scenario['code'],
        "description": scenario['desc'],
        "card_type": "RuPay Platinum"
    })

    return f"""
    Generate a JSON conversation about a specific RuPay card transaction failure.
    
    CONTEXT:
    - User Persona: {persona}
    - Scenario: {scenario['desc']} (RuPay Code {scenario['code']})
    - Date: {d['txn_date']}, Time: {d['txn_time']}, Amount: {rand_amt}, Card Last 4: {rand_last4}
    
    FLOW:
    1. User reports a failed transaction (at ATM or Online).
    2. Assistant asks for details (Card number, Amount, Date).
    3. User provides details.
    4. Assistant calls `get_rupay_transaction_status`.
    5. Tool returns the error details.
    6. Assistant explains the reason naturally to the user (e.g., "It seems your bank declined it due to...").
    
    REQUIRED JSON:
    {{
      "conversation_id": "RUPAY_TXN_{str(uuid.uuid4())[:8]}",
      "messages": [
        {{"role": "user", "content": "..."}},
        {{"role": "assistant", "content": "..."}},
        {{"role": "user", "content": "..."}},
        {{"role": "assistant", "content": null, "tool_calls": [{{"id": "{call_id}", "type": "function", "function": {{"name": "get_rupay_transaction_status", "arguments": "{{\\"date\\":\\"{d['txn_date']}\\",\\"approx_time\\":\\"{d['txn_time']}\\",\\"amount\\":{rand_amt},\\"card_last_4\\":\\"{rand_last4}\\"}}"}}}}]}},
        {{"role": "tool", "tool_call_id": "{call_id}", "content": "{tool_output.replace('"', '\\"')}"}},
        {{"role": "assistant", "content": "..."}},
        {{"role": "user", "content": "..."}}
      ],
      "metadata": {{ "Type": "Transaction", "Scenario": "{scenario['desc']}" }}
    }}
    Output ONLY Valid JSON.
    """

# ================= PROMPT 2: RAG (DOMAIN KNOWLEDGE) =================
def get_rag_prompt(topic, persona):
    call_id = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
    
    return f"""
    Generate a JSON conversation where the user asks a GENERAL QUESTION about RuPay cards.
    
    CONTEXT:
    - User Persona: {persona}
    - Question: "{topic['query']}"
    - Correct Answer (Context): "{topic['context']}"
    
    FLOW:
    1. User asks the question.
    2. Assistant calls `get_rupay_knowledge_base` with the query.
    3. Tool returns the Context Chunk.
    4. Assistant answers the user politely utilizing the tool output.
    
    REQUIRED JSON:
    {{
      "conversation_id": "RUPAY_RAG_{str(uuid.uuid4())[:8]}",
      "messages": [
        {{"role": "user", "content": "..."}},
        {{"role": "assistant", "content": null, "tool_calls": [{{"id": "{call_id}", "type": "function", "function": {{"name": "get_rupay_knowledge_base", "arguments": "{{\\"query\\":\\"{topic['query']}\\"}}"}}}}]}},
        {{"role": "tool", "tool_call_id": "{call_id}", "content": "{{\\"chunks\\": [\\"{topic['context']}\\"]}}"}},
        {{"role": "assistant", "content": "..."}}
      ],
      "metadata": {{ "Type": "RAG", "Topic": "{topic['intent']}" }}
    }}
    Output ONLY Valid JSON.
    """

# ================= BALANCING LOGIC =================
def get_balanced_scenarios(total_needed):
    # We only need half the total for transactions (since other half is RAG)
    txn_needed = math.ceil(total_needed / 2)
    queue = []
    full_sets = txn_needed // len(SCENARIOS)
    remainder = txn_needed % len(SCENARIOS)

    for _ in range(full_sets):
        queue.extend(SCENARIOS)
    if remainder > 0:
        queue.extend(random.sample(SCENARIOS, remainder))
    
    random.shuffle(queue)
    return queue

# ================= MAIN LOOP =================
dataset = []
txn_queue = get_balanced_scenarios(TARGET_COUNT)

print(f"Starting Generation: {TARGET_COUNT} Conversations (50% RuPay Txn, 50% RuPay RAG)...")

for i in range(TARGET_COUNT):
    persona = random.choice(PERSONAS)
    
    # === ALTERNATING LOGIC ===
    if i % 2 == 0:
        # EVEN INDEX: Generate Transaction (Tool Call)
        scenario = txn_queue[i // 2]
        prompt = get_transaction_prompt(scenario, persona)
        gen_type = f"Transaction [{scenario['code']}]"
    else:
        # ODD INDEX: Generate RAG (General Knowledge)
        topic = random.choice(RAG_TOPICS)
        prompt = get_rag_prompt(topic, persona)
        gen_type = f"RAG [{topic['intent']}]"

    # API Call
    payload = {
        "model": "/model",
        "messages": [
            {"role": "system", "content": "You are a synthetic data generator. Output strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 4096
    }

    try:
        print(f"Generating {i+1}/{TARGET_COUNT}: {gen_type}...")
        response = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {API_KEY}"})

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            if content.startswith("```"):
                content = content.replace("```json", "").replace("```", "").strip()
            
            json_obj = json.loads(content)
            if "messages" in json_obj:
                dataset.append(json_obj)
            else:
                print("Skipping invalid structure")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")

# Save
output_file = "rupay_mixed_training_data.jsonl"
with open(output_file, "w") as f:
    for entry in dataset:
        f.write(json.dumps(entry) + "\n")

print(f"Successfully saved {len(dataset)} conversations to {output_file}")