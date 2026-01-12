"""
RAG AGENT - Agent Interface for RAG System
Provides the agent interface that integrates with the main orchestration system.
Uses the new modular RAG pipeline architecture.
"""

import json
import os

try:
    from core.rag_pipeline import RupayRAG
except ImportError:
    RupayRAG = None


# CLASS NAME MUST BE EXACTLY 'RAGAgent'
class RAGAgent:
    """
    Agent interface for the RAG system.
    Integrates with the main agent orchestration system.
    """
    
    def __init__(self):
        """Initialize the RAG agent with the new pipeline."""
        if RupayRAG:
            try:
                # Initialize new RAG pipeline (no API key needed - uses custom endpoint)
                self.rag = RupayRAG()
                
                # Check if offline phase is complete
                system_info = self.rag.get_system_info()
                
                if system_info['offline_ready']:
                    print(f"[RAGAgent] ✅ RAG Pipeline initialized successfully")
                    print(f"[RAGAgent] Loaded {system_info.get('num_chunks', 0)} chunks from {system_info.get('num_documents', 0)} documents")
                else:
                    print("[RAGAgent] ⚠️  Offline ingestion not complete. Please run offline ingestion first.")
                    print("[RAGAgent] The agent will return error messages until documents are ingested.")
                
            except Exception as e:
                print(f"[RAGAgent] ❌ Error initializing RAG: {e}")
                self.rag = None
        else:
            print("[RAGAgent] ❌ RAG Pipeline module not found.")
            self.rag = None

    def execute(self, params):
        """
        Execute a RAG query.
        
        Input: {'query': 'what is the limit'}
        Output: JSON string with answer and chunks
        
        Returns:
            JSON string with format:
            {
                "answer": "...",  # Generated answer
                "chunks": ["...", "..."],  # Retrieved text chunks
                "num_chunks": 3  # Number of chunks used
            }
        """
        query = params.get("query", "")
        
        if not query:
            return json.dumps({
                "answer": "Please provide a question.",
                "chunks": [],
                "num_chunks": 0
            })
        
        print(f"[RAGAgent] Processing query: {query}")

        if not self.rag:
            return json.dumps({
                "answer": "System Error: RAG Pipeline is not active.",
                "chunks": [],
                "num_chunks": 0,
                "error": "RAG pipeline not initialized"
            })
        
        try:
            # Use new query method that returns answer + chunks
            result = self.rag.query(
                query, 
                return_context=False,  # Don't need raw context
                return_metadata=False   # Don't need detailed metadata
            )
            
            # Extract answer and chunks
            answer = result.get('answer', '')
            documents = result.get('documents', [[]])[0]  # ChromaDB format compatibility
            num_chunks = result.get('num_chunks', 0)
            
            # Check if we got a valid answer
            if not documents and num_chunks == 0:
                response = {
                    "answer": answer if answer else "I couldn't find specific information about that in the RuPay documents.",
                    "chunks": [],
                    "num_chunks": 0
                }
            else:
                response = {
                    "answer": answer,
                    "chunks": documents[:3],  # Return top 3 chunks for reference
                    "num_chunks": num_chunks
                }
            
            print(f"[RAGAgent] ✅ Query processed: {num_chunks} chunks used, answer length: {len(answer)} chars")
            
            return json.dumps(response)
            
        except Exception as e:
            print(f"[RAGAgent] ❌ Error processing query: {e}")
            return json.dumps({
                "answer": f"Error processing your question: {str(e)}",
                "chunks": [],
                "num_chunks": 0,
                "error": str(e)
            })
