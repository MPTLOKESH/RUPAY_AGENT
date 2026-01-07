import json

# CLASS NAME MUST BE EXACTLY 'RAGAgent'
class RAGAgent:
    def __init__(self):
        # In a real system, you would load FAISS/ChromaDB here.
        # This is a simulated knowledge base for your 500 training examples.
        self.knowledge_base = [
            {"keys": ["what is", "define", "meaning", "full form"], "text": "RuPay is a domestic card payment network developed by the National Payments Corporation of India (NPCI) to provide a secure and affordable payment infrastructure."},
            {"keys": ["limit", "max amount", "withdraw limit", "cap"], "text": "For contactless transactions, the network mandates that a PIN is not required for transactions up to ₹5,000; any amount above this requires PIN authentication."},
            {"keys": ["fail", "deducted", "reversal", "money cut"], "text": "If money is deducted but the transaction failed, it is usually reversed within T+5 working days automatically. If not, contact your bank with the RRN."},
            {"keys": ["balance", "check", "enquiry"], "text": "You can check your balance using the RuPay Balance Enquiry feature at any ATM or supported Point of Sale (POS) terminal. While the RuPay network supports this transaction type universally, specific limits on the number of free balance checks are determined by your issuing bank."}
        ]

    def execute(self, params):
        """
        Input: {'query': 'what is the limit'}
        Output: JSON string with chunks
        """
        query = params.get("query", "").lower()
        print(f"[RAGAgent] Searching for: {query}")

        best_match = "I couldn't find specific info in the knowledge base."
        max_score = 0

        # Simple Keyword Matching Logic
        for item in self.knowledge_base:
            score = sum(1 for k in item["keys"] if k in query)
            if score > max_score:
                max_score = score
                best_match = item["text"]

        return json.dumps({"chunks": [best_match]})