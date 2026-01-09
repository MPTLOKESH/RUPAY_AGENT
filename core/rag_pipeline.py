import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import re

# Model Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_FILE = "data/rupay_faiss.index"
METADATA_FILE = "data/rupay_metadata.pkl"

class RupayRAG:
    def __init__(self):
        """
        Initialize RAG with FAISS and SentenceTransformer.
        """
        print("[RAG] Loading Embedding Model...")
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        
        # Load existing index if available
        if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
            print("[RAG] Loading existing FAISS index...")
            self.index = faiss.read_index(INDEX_FILE)
            with open(METADATA_FILE, "rb") as f:
                self.chunks = pickle.load(f)
        else:
            print("[RAG] Creating new FAISS index...")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = [] # List to store text corresponding to vectors

    def extract_text_from_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            result = page.extract_text()
            if result:
                text += result + "\n"
        return text

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def split_text(self, text, chunk_size=500, overlap=50):
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap 
        return chunks

    def ingest_document(self, file_path):
        print(f"Loading document: {file_path}")
        text = self.extract_text_from_pdf(file_path)
        cleaned_text = self.clean_text(text)
        new_chunks = self.split_text(cleaned_text)
        print(f"Created {len(new_chunks)} chunks.")

        # Embed chunks
        print("Generating embeddings...")
        embeddings = self.model.encode(new_chunks)
        
        # Add to FAISS Index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store text chunks
        self.chunks.extend(new_chunks)
        
        # Save to disk
        faiss.write_index(self.index, INDEX_FILE)
        with open(METADATA_FILE, "wb") as f:
            pickle.dump(self.chunks, f)
            
        print("Ingestion complete and saved.")

    def query(self, query_text, n_results=3):
        """
        Returns format compatible with previous Chroma implementation:
        {'documents': [[text1, text2, ...]]}
        """
        query_vector = self.model.encode([query_text])
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), n_results)
        
        results = []
        for idx in indices[0]:
            if idx < len(self.chunks):
                results.append(self.chunks[idx])
        
        return {'documents': [results]}

if __name__ == "__main__":
    # Ingestion Script
    pdf_file = "data/rupay_document.pdf" 
    rag = RupayRAG()
    
    if os.path.exists(pdf_file):
        rag.ingest_document(pdf_file)
        
        test_q = "What are the benefits of RuPay?"
        print(f"\nTest Query: {test_q}")
        res = rag.query(test_q)
        print(res['documents'][0][0])
    else:
        print(f"File not found: {pdf_file}")
