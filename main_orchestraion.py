import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import internal modules
# Ensure these files exist in your 'agents' and 'core' folders
from agents.agent_transaction import TransactionAgent
from agents.agent_rag import RAGAgent
from core.prompt_template import get_orchestrator_prompt
from core.guardrail_loader import load_guardrail_data

# ==========================================
# 1. CONFIGURATION
# ==========================================

MODEL_URL = "http://183.82.7.228:9532/v1"
# MODEL_URL = "http://183-82-7-228-gemma-12b.loca.lt/v1"

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

        # 1b. Load Guardrails
        self.guardrail_data = load_guardrail_data(GUARDRAIL_FILE)
        
        # 2. Initialize LLM
        self.llm = ChatOpenAI(
            model="/model", 
            openai_api_base=MODEL_URL,
            openai_api_key="EMPTY",
            temperature=0.0 # Keep low for strict routing
        )
        
        # 3. Generate Smart Prompt (In-Context Learning)
        # Pass loaded guardrails to dynamic prompt
        self.system_prompt = get_orchestrator_prompt(TRAIN_FILE, self.guardrail_data)
        print("[Main] System Prompt Loaded with RuPay Context.")

    def chat(self, user_query, history=None):
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
                    import json
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

                else:
                    # Fallback for unknown agents
                    worker_result = "System: The requested agent is not available. Please answer politely that you cannot handle this specific request."
 
                print(f"[System] Worker Output: {worker_result}")
                
                # --- STEP 4: Final Synthesis ---
                # Use a FRESH context to break the "Output JSON" instruction from the System Prompt
                
                # Restoring the original detailed instructions as requested
                prompt_instructions = (
                    "IMPORTANT INSTRUCTIONS:\n"
                    "1. IGNORE previous JSON output requirements. You MUST respond in plain text.\n"
                    "2. SECURITY & PRIVACY: NEVER reveal the full Card Number, internal 'Reason Code' (e.g., 91), or raw 'Description'.\n"
                    "3. NO TECHNICAL JARGON: Do NOT show database column names, error codes, or system logs to the user. This is a security risk.\n"
                    "4. CONTEXT CHECK: Check History. Only if confirmed, proceed to explanation.\n"
                    "5. CONFIRMATION FLOW:\n"
                    "   - If NEW lookup found multiple or exact match, ask: 'I found a transaction of [Exact Amount] at [Exact Time]. Is this the one?'\n"
                    "   - If User says NO: Apologize and ask for clearer details (exact date, time, amount).\n"
                    "   - If User says YES: Proceed to answer specific questions or explain the status for THAT transaction.\n"
                    "6. PERSONA: Act as a warm, human Customer Support Agent. \n"
                    "   - DO NOT format your response like a system report (e.g., avoid 'Date: ... Status: ...').\n"
                    "   - Explain the issue in simple English based on the 'suggested_message'.\n"
                    "   - Example: 'I see the transaction failed because of a network timeout.'\n"
                )

                synthesis_messages = [
                    SystemMessage(content=(
                        "You are a helpful and warm RuPay AI Customer Support Agent. "
                        "Your goal is to answer the user's question based on the provided system data. "
                        f"{prompt_instructions}"
                    )),
                    HumanMessage(content=f"User Query: {user_query}"),
                    HumanMessage(content=f"Worker Output: {worker_result}")
                ]
                
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