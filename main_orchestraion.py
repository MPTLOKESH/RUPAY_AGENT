import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import internal modules
# Ensure these files exist in your 'agents' and 'core' folders
from agents.agent_transaction import TransactionAgent
from agents.agent_rag import RAGAgent
from agents.agent_guardrail import GuardrailAgent
from core.prompt_template import get_orchestrator_prompt
from core.guardrail_loader import load_guardrail_data

# ==========================================
# 1. CONFIGURATION
# ==========================================

MODEL_URL = "http://183.82.7.228:9532/v1"
# MODEL_URL = "http://183-82-7-228-9520-gemma12b.loca.lt/v1"

# Database Config (Docker)
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",  # <--- IMPORTANT: Using 5432 for Docker
    "user": "admin",
    "password": "adminpassword",
    "dbname": "rupay_transactions" # <--- Updated to RuPay DB
}

# File Paths
MAPPING_FILE = "data/desc_mapping.json"
GUARDRAIL_FILE = "data/guardrails_all_questions_1.txt"
TRAIN_FILE = "data/rupay_sft_2.json" # <--- Updated to RuPay Training Data

# ==========================================
# 2. ORCHESTRATOR CLASS
# ==========================================

class MainOrchestrator:
    def __init__(self):
        print("--- Initializing RuPay Orchestrator ---")
        
        # 1. Initialize Workers
        self.tx_worker = TransactionAgent(DB_CONFIG, MAPPING_FILE)
        self.rag_worker = RAGAgent()
        
        # 1b. Initialize Guardrail Agent (Pre-Filter)
        self.guardrail_agent = GuardrailAgent(GUARDRAIL_FILE)
        self.guardrail_data = self.guardrail_agent.guardrail_data
        
        # 2. Initialize LLM
        self.llm = ChatOpenAI(
            model="/model", 
            openai_api_base=MODEL_URL,
            openai_api_key="EMPTY",
            temperature=0.0 # Keep low for strict routing
        )
        
        # self.llm = ChatOpenAI(
        #     model="gemma-3-12b-it-merged", 
        #     openai_api_base=MODEL_URL,
        #     openai_api_key="EMPTY",
        #     temperature=0.0 # Keep low for strict routing
        # )
        

        # 3. Generate Smart Prompt (In-Context Learning)
        # Pass loaded guardrails to dynamic prompt
        self.system_prompt = get_orchestrator_prompt(TRAIN_FILE, self.guardrail_data)
        print("[Main] System Prompt Loaded with RuPay Context.")

    def chat(self, user_query, history=None):
        # --- GUARDRAIL PRE-CHECK ---
        # First, check if the query violates any guardrails
        # Pass history for context-aware checking
        guardrail_result = self.guardrail_agent.check_query(user_query, history)
        
        if not guardrail_result["is_safe"]:
            # Query triggered guardrails - return refusal message
            category = guardrail_result.get("category", "Safety Guidelines")
            message = guardrail_result.get("message", "I cannot assist with that request.")
            
            print(f"[Main] ⚠️ Guardrail triggered: {category}")
            return message
        
        # Query is safe - proceed with normal processing
        print(f"[Main] ✓ Guardrail check passed")
        
        # --- PREPARE MESSAGES WITH MEMORY ---
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add Conversation History (Deep Context)
        if history:
            for msg in history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # Add Current Query
        messages.append(HumanMessage(content=user_query))
        
        print(f"\nUser: {user_query}")
        
        # --- STEP 1: LLM Decides Strategy ---
        try:
            response = self.llm.invoke(messages)
            content = response.content
            
            # Clean up Markdown if present (e.g., ```json ... ```)
            if "```" in content:
                content = content.replace("```json", "").replace("```", "").strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            print(f"[ERROR] LLM Invoke failed: {str(e)}")
            
            # Smart fallback routing based on query content
            query_lower = user_query.lower()
            
            # Check for common patterns and route appropriately
            if any(word in query_lower for word in ['upi', 'nach', 'imps', 'rtgs', 'neft', 'visa', 'mastercard']):
                # Non-RuPay transaction
                return "I can only assist with RuPay transaction issues and general banking queries."
            
            elif any(word in query_lower for word in ['transaction', 'failed', 'txn', 'payment', 'withdrawal', 'deposit']):
                # Likely transaction query - ask for details
                return "I can help you check your failed transaction. Please provide: date, amount, card last 4 digits, and approximate time."
            
            elif any(word in query_lower for word in ['what', 'how', 'when', 'why', 'benefit', 'limit', 'card', 'rupay']):
                # Likely general question - route to RAG
                try:
                    worker_result = self.rag_worker.execute({"query": user_query})
                    # Parse RAG response
                    rag_data = json.loads(worker_result)
                    if rag_data.get('answer'):
                        return rag_data['answer']
                    elif rag_data.get('chunks'):
                        return rag_data['chunks'][0] if rag_data['chunks'] else "I couldn't find specific information about that."
                except:
                    return "I'm experiencing technical difficulties. Could you rephrase your question?"
            
            else:
                # Generic fallback
                return "I apologize, but I'm experiencing technical difficulties. I can assist with RuPay transaction issues or answer questions about RuPay services. Please try rephrasing your query."
        
        # --- STEP 2: Check for JSON Command ---
        # Robust Strategy: Find first '{' and last '}'
        # This handles nested JSON objects unlike the simple regex
        
        json_str = None
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx : end_idx + 1]
        
        if json_str:
            try:
                # Normalizing quotes is risky if text contains apostrophes.
                # Only minimal cleanup if absolutely necessary, but standard LLM JSON should be valid.
                try:
                    command = json.loads(json_str)
                except json.JSONDecodeError:
                    # Fallback: Try fixing single quotes only if standard parse fails
                    fixed_str = json_str.replace("'", '"')
                    command = json.loads(fixed_str)
                    
                target = command.get("target")
                params = command.get("parameters")
                
                print(f"[Main] Routing to -> {target}")
                
                # --- STEP 3: Execute Worker ---
                worker_result = ""
                
                if target == "tool_agent":
                    # SQL / Transaction Lookup
                    worker_result = self.tx_worker.execute(params)
                    
                elif target == "rag_agent":
                    # General Q&A
                    worker_result = self.rag_worker.execute(params)

                elif target == "identity_agent":
                    # Greetings & Identity
                    msg_type = params.get("type", "greeting")
                    if msg_type == "greeting":
                        return "Hello! I am your RuPay AI Assistant. I can help you check failed transactions or answer questions about RuPay services."
                    else:
                        return "I am an AI agent powered by RuPay. I can verify transaction statuses and assist with general banking queries."
                
                elif target == "guardrail_agent":
                    # Guardrails - Return Specific Refusal
                    category = params.get("category", "General")
                    
                    # Refusal Messages from User's Policy (Loaded from File)
                    if hasattr(self, 'guardrail_data') and self.guardrail_data:
                        # Normalize category matching (Title Case)
                        search_cat = category.replace("_", " ").title()
                        
                        # Use loaded message or fallback
                        worker_result = self.guardrail_data.get(search_cat, "I cannot assist with that request due to safety guidelines.")
                    else:
                        worker_result = "I cannot assist with that request due to safety guidelines."
                    
                    return worker_result

                elif target == "reject":
                    # Irrelevant Query
                    return "I can only assist with RuPay transaction issues and general banking queries."

                elif target == "direct_reply":
                    # Router wants to ask a question directly (e.g. missing params)
                    return params.get("message", "Could you please clarify?")

                else:
                    # Fallback for unknown agents
                    worker_result = "System: The requested agent is not available. Please answer politely that you cannot handle this specific request."
 
                print(f"[System] Worker Output: {worker_result}")
                
                # --- STEP 4: Final Synthesis ---
                # Use a FRESH context to break the "Output JSON" instruction from the System Prompt
                
                # Enhanced instructions for confirmation flow and follow-ups
                prompt_instructions = (
                    "IMPORTANT INSTRUCTIONS:\n"
                    "1. IGNORE previous JSON output requirements. You MUST respond in plain text.\n"

                    "2. SECURITY & PRIVACY:\n"
                    "   - NEVER reveal the full Card Number, internal 'Reason Code' (e.g., 91), or raw 'Description'.\n"
                    "   - NEVER expose internal system terms, logs, or identifiers.\n"

                    "3. NO TECHNICAL JARGON:\n"
                    "   - Do NOT show database column names, error codes, or system logs to the user.\n"
                    "   - Use simple, customer-friendly language only.\n"

                    "4. DOMAIN PERMISSION (VERY IMPORTANT):\n"
                    "   - This assistant is ALLOWED to answer DOMAIN-RELATED QUESTIONS about RuPay and ALL NPCI products.\n"
                    "   - NPCI products include but are not limited to: RuPay, UPI, NACH, FASTag/NETC, IMPS, AEPS, BBPS.\n"
                    "   - Domain questions are ALLOWED EVEN IF they are:\n"
                    "     * Single-word queries (e.g., 'upi', 'npci', 'nach')\n"
                    "     * Short or incomplete questions (e.g., 'limit?', 'charges?', 'how works?')\n"
                    "     * Abbreviated or conversational follow-ups\n"
                    "   - Such queries MUST be answered as valid domain questions.\n"
                    "   - DO NOT block, reject, or force transaction lookup for domain-only queries.\n"

                    "5. CONVERSATION HISTORY & SHORT QUERIES:\n"
                    "   - Always review conversation history for context.\n"
                    "   - Short follow-up queries like 'status?', 'why failed?', 'same one?', 'upi?' are VALID.\n"
                    "   - Use prior context to interpret these correctly.\n"

                    "6. TRANSACTION CONFIRMATION FLOW (ONLY WHEN TRANSACTION DATA EXISTS):\n"
                    "   - Apply this flow ONLY if transaction data is present in Worker Output.\n"
                    "   - If this is the FIRST time a transaction is identified, ask:\n"
                    "     'I found a transaction of ₹[Exact Amount] at [Exact Time] on [Date]. Is this the one you're asking about?'\n"
                    "   - If the amounts differ slightly (e.g., user said 33k, found 33.8k), MENTION this: 'I found a similar transaction of ₹...' \n"
                    "   - If the user says NO: Apologize and ask for clearer details (exact date, time, amount).\n"
                    "   - If the user says YES: Mark the transaction as confirmed and proceed. DO NOT re-verify the amount difference.\n"

                    "7. FOLLOW-UP QUESTIONS (AFTER TRANSACTION CONFIRMATION):\n"
                    "   - If the user asks follow-ups like 'why did it fail?', 'what should I do?', 'can you explain?':\n"
                    "     * DO NOT ask for confirmation again\n"
                    "     * Use ONLY the data from Worker Output\n"
                    "     * Base explanations on 'suggested_message' or 'error_reason'\n"
                    "     * NEVER invent or assume information\n"

                    "8. MIXED DOMAIN + TRANSACTION QUERIES:\n"
                    "   - If the user asks both a transaction question and an NPCI domain question:\n"
                    "     * Answer the transaction part using Worker Output\n"
                    "     * Answer the domain part using general NPCI knowledge\n"

                    "9. PERSONA:\n"
                    "   - Act as a warm, polite, human Customer Support Agent.\n"
                    "   - DO NOT format responses like system reports (avoid 'Date:', 'Status:', etc.).\n"
                    "   - Explain issues naturally, as a support executive would.\n"

                    "10. ACCURACY:\n"
                    "   - Use ONLY Worker Output for transaction-specific details.\n"
                    "   - Use general knowledge ONLY for NPCI domain explanations.\n"
                    "   - NEVER hallucinate, guess, or fabricate transaction data.\n"
                )


                # Build synthesis messages with conversation history for context
                synthesis_messages = [
                    SystemMessage(content=(
                        "You are a helpful and warm RuPay AI Customer Support Agent. "
                        "Your goal is to answer the user's question based on the provided system data and conversation history. "
                        f"{prompt_instructions}"
                    )),
                ]
                
                # Add recent conversation history (last 4 messages) for context
                if history:
                    recent_history = history[-4:] if len(history) > 4 else history
                    for msg in recent_history:
                        role = msg.get("role")
                        content = msg.get("content")
                        if role == "user":
                            synthesis_messages.append(HumanMessage(content=f"[Previous User]: {content}"))
                        elif role == "assistant":
                            synthesis_messages.append(AIMessage(content=f"[Previous Assistant]: {content}"))
                
                # Add current query and worker output
                synthesis_messages.append(HumanMessage(content=f"Current User Query: {user_query}"))
                synthesis_messages.append(HumanMessage(content=f"Worker Output (Transaction Data): {worker_result}"))
                
                final_response = self.llm.invoke(synthesis_messages)
                final_content = final_response.content

                # Final Safeguard: If output still looks like JSON, return a friendly error
                if final_content.strip().startswith("{") and '"target":' in final_content:
                    return "I apologize, but I couldn't process that request correctly. Could you please rephrase?"

                return final_content

            except json.JSONDecodeError:
                return f"Error: LLM generated invalid JSON.\nRaw output: {content}"
            except Exception as e:
                return f"Error during worker execution: {str(e)}"
        else:
            # If no JSON command found, return the raw text (Conversational)
            return content

# ==========================================
# RUN THE AGENT (TESTING)
# ==========================================
if __name__ == "__main__":
    bot = MainOrchestrator()

    # Test 1: RAG (General Question)
    print("\n--- TEST 1 (RAG) ---")
    print(bot.chat("What is the transaction limit for RuPay contactless cards?"))

    # Test 2: Transaction (SQL Lookup)
    # Note: Use a date/amount that exists in your 'RuPay_Transaction_Dummy_Data.xlsx'
    print("\n--- TEST 2 (Transaction) ---")
    print(bot.chat("Check my failed transaction of 5000 rupees on 2025-05-10. Card ending in 4455."))