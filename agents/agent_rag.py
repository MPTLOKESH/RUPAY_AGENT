import json
try:
    from core.rag_pipeline import RupayRAG
except ImportError:
    RupayRAG = None

# CLASS NAME MUST BE EXACTLY 'RAGAgent'
class RAGAgent:
    def __init__(self):
        # Initialize Real RAG Pipeline
        if RupayRAG:
            try:
                self.rag = RupayRAG()
                print("[RAGAgent] RAG Pipeline Initialized Successfully.")
            except Exception as e:
                print(f"[RAGAgent] Error Initializing RAG: {e}")
                self.rag = None
        else:
            print("[RAGAgent] RAG Pipeline Module Not Found.")
            self.rag = None

    def execute(self, params):
        """
        Input: {'query': 'what is the limit'}
        Output: JSON string with chunks
        """
        query = params.get("query", "")
        print(f"[RAGAgent] Searching for: {query}")

        if not self.rag:
            return json.dumps({"chunks": ["System Error: RAG Pipeline is not active."]})
        
        try:
            # Retrieve 3 most relevant chunks
            results = self.rag.query(query, n_results=3)
            
            # Extract text from results dict: {'ids': [...], 'documents': [[chunk1, chunk2]], ...}
            # ChromaDB returns documents as a list of lists (one list per query).
            documents = results.get('documents', [[]])[0]
            
            if not documents:
                return json.dumps({"chunks": ["I couldn't find specific info in the Rupay documents."]})
                
            return json.dumps({"chunks": documents})
            
        except Exception as e:
            return json.dumps({"chunks": [f"Error searching documents: {str(e)}"]})