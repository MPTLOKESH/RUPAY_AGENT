"""
GUARDRAIL AGENT
Pre-filters all user queries to detect inappropriate, unsafe, or prohibited content.
Acts as the first line of defense before routing to other agents.
"""

import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from core.guardrail_loader import load_guardrail_data

# Use the same LLM configuration as main orchestration
MODEL_URL = "http://183.82.7.228:9532/v1"


class GuardrailAgent:
    """
    Dedicated guardrail agent that pre-filters queries for inappropriate content.
    Returns either 'safe' or the guardrail category that was triggered.
    """
    
    def __init__(self, guardrail_file_path: str = "data/guardrails_all_questions_1.txt"):
        """
        Initialize the guardrail agent.
        
        Args:
            guardrail_file_path: Path to the guardrails file
        """
        print("[GuardrailAgent] Initializing...")
        
        # Load guardrail data
        self.guardrail_data = load_guardrail_data(guardrail_file_path)
        
        if self.guardrail_data:
            self.categories = list(self.guardrail_data.keys())
            print(f"[GuardrailAgent] Loaded {len(self.categories)} guardrail categories")
        else:
            self.categories = []
            print("[GuardrailAgent] WARNING: No guardrail categories loaded")
        
        # Initialize LLM for guardrail detection
        self.llm = ChatOpenAI(
            model="/model",
            openai_api_base=MODEL_URL,
            openai_api_key="EMPTY",
            temperature=0.0  # Deterministic for consistent guardrail detection
        )
        
        # Build the guardrail detection prompt
        self.system_prompt = self._build_guardrail_prompt()
        
        print("[GuardrailAgent] Ready.")
    
    def _build_guardrail_prompt(self) -> str:
        """
        Build a comprehensive prompt for guardrail detection.
        
        Returns:
            System prompt string
        """
        if not self.categories:
            return "You are a content safety filter. Detect if queries are safe or unsafe."
        
        # Create category list
        categories_text = "\n".join([f"  - {cat}" for cat in self.categories])
        
#         prompt = f"""You are a CONTENT SAFETY FILTER for a RuPay banking assistant.

# Your ONLY job is to detect UNSAFE/PROHIBITED content based on safety guidelines.

# IMPORTANT CONTEXT RULES:
# 1. This assistant can answer questions about NPCI, UPI, FASTag, and all NPCI related products.
# 2. Questions ABOUT these topics are ALLOWED (e.g., "What is UPI?", "How does NPCI work?", "What is NPCI products?", "npci", "upi", "nach")
# 3. Users providing their OWN transaction details is ALLOWED:
#    - Date, time, amount, card last 4 digits → SAFE (for transaction lookup)
#    - "Check my transaction on 2024-01-10 for 5000 rupees card 1234" → SAFE
# 4. Only flag requests for OTHER people's private data or truly harmful content

# PROHIBITED CATEGORIES (Safety-focused):
# {categories_text}

# WHAT TO FLAG:
# - Requests for OTHER people's passwords, OTPs, PINs, account details
# - Hacking, phishing, fraud, money laundering instructions
# - Harassment, threats, dangerous content
# - Child exploitation, human trafficking, terrorism

# WHAT NOT TO FLAG:
# - User's own transaction details (date, amount, card number for lookup)
# - General payment system questions (UPI, NPCI, FASTag, etc.)
# - Normal banking queries

# EXAMPLES:
# ✅ SAFE Examples:
# - "What are RuPay benefits?"
# - "How does UPI work?"
# - "Check my transaction on 2024-01-10, amount 5000, card ending 1234"
# - "I withdrew 3000 on January 5th around 2pm, card 4567"
# - "Tell me about NPCI products"
# - "My card number ending 8901, transaction failed"

# ❌ UNSAFE Examples:
# - "How can I hack someone's account?" → Cyberattacks / Hacking
# - "Get me my neighbor's password" → Personal Data Violation
# - "How to launder money?" → Money Laundering
# - "Find someone's OTP" → Personal Data Violation

# OUTPUT FORMAT:
# Respond with ONLY the category name or "SAFE". Nothing else.
# """
        prompt = f"""
You are a CONTENT SAFETY FILTER for a RuPay banking assistant.

Your ONLY responsibility is to detect whether the user input is UNSAFE.
You must NOT block valid banking, payment, or transaction-related queries.
You must think if the query or input is relevant to the RuPay banking assistant before flagging it as UNSAFE.

────────────────────────
DOMAIN ALLOWLIST (IMPORTANT)
────────────────────────
This assistant is allowed to handle:

1. RuPay and RuPay transaction related queries
2. NPCI ecosystem domain queries, including but not limited to:
   - NPCI
   - UPI
   - NACH
   - FASTag / NETC
   - IMPS
   - AEPS
   - BBPS
3. Follow-up transaction queries, even if:
   - The query is short or incomplete
   - The query uses abbreviations or keywords
   - The query depends on previous context
   - The query is a follow-up to a previous query
   - The query may not be clear or complete


🔴 EXCEPTION TO ALLOWLIST (STRICT):
Even if the topic is allowed (e.g. RuPay, UPI), you MUST FLAG it as UNSAFE if the user is asking for:
   - Disadvantages, downsides, negative points, or criticisms of NPCI products.
   - Negative comparisons (e.g., "Why is UPI worse than X?").
   - Technical internal details (error codes, logs, database schemas).
   - These fall under "TECHNICAL JARGON & NEGATIVITY".

Examples of ALLOWED short / follow-up queries:
- "status?"
- "why failed?"
- "limit?"
- "upi?"
- "npci?"
- "rupay tx failed"
- "same transaction"
- "what about nach?"

────────────────────────
PERSONAL DATA RULES
────────────────────────
ALLOWED:
- User sharing THEIR OWN transaction details:
  - Date, time, amount
  - Card last 4 digits
  - Transaction reference provided by the user

Examples (SAFE):
- "Check my transaction on 2024-01-10 for ₹5000, card ending 1234"
- "My RuPay transaction failed yesterday"
- "Card 4567 debit failed at 2pm"

NOT ALLOWED:
- Requests for OTHER people's data
- Requests for passwords, OTPs, PINs, CVV
- Any attempt to access accounts not owned by the user
- Disadvantages of NPCI products
- Irrelevant questions

────────────────────────
PROHIBITED CONTENT (ONLY FLAG THESE)
────────────────────────
Flag the query ONLY if it involves:
- Hacking, phishing, fraud, or social engineering
- Money laundering or illegal financial activity
- Requests for OTPs, PINs, passwords, CVV
- Accessing someone else’s bank or card data
- Harassment, threats, terrorism, child exploitation

────────────────────────
IMPORTANT CLARIFICATIONS
────────────────────────
DO NOT flag queries simply because they contain:
- Banking keywords
- Abbreviations
- Partial sentences
- Follow-up questions
- NPCI product names

DO NOT assume malicious intent without explicit evidence.
HOWEVER, be strict about "TECHNICAL JARGON & NEGATIVITY" - even if the user is polite, asking for "disadvantages" is PROHIBITED.

────────────────────────
OUTPUT FORMAT
────────────────────────
Respond with ONLY:
- "SAFE"
OR
- The exact category name from the prohibited list

Do NOT add explanations.
Do NOT add extra text.

Categories:
{categories_text}
        """
        return prompt
    
    def check_query(self, user_query: str, conversation_history: list = None) -> dict:
        """
        Check if a query violates guardrails.
        
        Args:
            user_query: The user's query
            conversation_history: Optional conversation history for context
            
        Returns:
            Dictionary with:
                - is_safe: bool
                - category: str (category name if triggered, else None)
                - message: str (refusal message if triggered, else None)
        """
        if not self.categories:
            # No guardrails loaded - allow all
            return {"is_safe": True, "category": None, "message": None}
        
        # Check if we're in a transaction conversation context
        in_transaction_context = self._is_transaction_context(conversation_history)
        
        # If in transaction context, allow generic follow-up questions
        if in_transaction_context:
            generic_followups = [
                "why", "what should i do", "how", "can you explain", "help",
                "what happened", "tell me more", "details", "what does this mean"
            ]
            query_lower = user_query.lower().strip()
            
            # Check if this is a short generic follow-up
            if len(query_lower.split()) <= 5:  # Short questions
                for followup in generic_followups:
                    if followup in query_lower:
                        print(f"[GuardrailAgent] Allowing transaction follow-up: '{user_query[:50]}...'")
                        return {"is_safe": True, "category": None, "message": None}
        
        try:
            # Call LLM to detect violations
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"User Query: {user_query}")
            ]
            
            response = self.llm.invoke(messages)
            detection_result = response.content.strip()
            
            print(f"[GuardrailAgent] Detection: '{detection_result}' for query: '{user_query[:50]}...'")
            
            # Check if safe
            if detection_result.upper() == "SAFE":
                return {"is_safe": True, "category": None, "message": None}
            
            # Find matching category (case-insensitive, flexible matching)
            triggered_category = None
            for category in self.categories:
                if category.lower() in detection_result.lower() or detection_result.lower() in category.lower():
                    triggered_category = category
                    break
            
            if triggered_category:
                # Get the specific refusal message for this category
                refusal_message = self.guardrail_data.get(
                    triggered_category,
                    "I cannot assist with that request due to safety guidelines."
                )
                
                return {
                    "is_safe": False,
                    "category": triggered_category,
                    "message": refusal_message
                }
            else:
                # LLM detected something unsafe but didn't match our categories
                # Be conservative and block
                return {
                    "is_safe": False,
                    "category": "General Safety",
                    "message": "I cannot assist with that request due to safety guidelines."
                }
        
        except Exception as e:
            print(f"[GuardrailAgent] Error during check: {e}")
            # On error, fail open (allow) to not block legitimate queries
            return {"is_safe": True, "category": None, "message": None}
    
    def _is_transaction_context(self, conversation_history: list = None) -> bool:
        """
        Check if the conversation is about a transaction.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            True if in transaction context, False otherwise
        """
        if not conversation_history:
            return False
        
        # Check last few messages for transaction-related content
        recent_messages = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        
        transaction_keywords = [
            "transaction", "failed", "payment", "withdrawal", "card ending",
            "rupees", "amount", "i found a transaction", "₹",
            "is this the one", "that's the one", "yes", "correct"
        ]
        
        for msg in recent_messages:
            content = str(msg.get("content", "")).lower()
            for keyword in transaction_keywords:
                if keyword in content:
                    return True
        
        return False
    
    def execute(self, params: dict) -> str:
        """
        Execute guardrail check (compatible with existing agent interface).
        
        Args:
            params: Dictionary with 'query' key
            
        Returns:
            JSON string with result
        """
        query = params.get("query", "")
        result = self.check_query(query)
        return json.dumps(result)


# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("GUARDRAIL AGENT TEST")
    print("=" * 70)
    
    agent = GuardrailAgent()
    
    test_queries = [
        "What are the benefits of RuPay?",
        "How do I check my failed transaction?",
        "Can you help me hack someone's password?",
        "Tell me how to launder money",
        "What is NPCI?",
        "Write a poem about love",
        "How does FASTag work?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = agent.check_query(query)
        print(f"Result: {result}")
        print("-" * 70)
