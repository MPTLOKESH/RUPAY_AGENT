"""
ONLINE RETRIEVAL MODULE
Handles the online query processing and retrieval:
1. Question preprocessing
2. Query embedding generation
3. Vector similarity search
4. Re-ranking of results
5. Context construction
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
import re
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import tiktoken

# Import configuration
from core.rag_config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    VECTOR_INDEX_FILE,
    METADATA_FILE,
    INITIAL_RETRIEVAL_K,
    RERANK_TOP_K,
    RERANK_MIN_SCORE,
    MAX_CONTEXT_TOKENS,
    TIKTOKEN_ENCODING,
    VERBOSE
)


class OnlineRetrieval:
    """
    Handles online retrieval and re-ranking of relevant chunks.
    This runs for every user query.
    """
    
    def __init__(self):
        """Initialize the retrieval pipeline."""
        if VERBOSE:
            print("[ONLINE] Initializing Retrieval Pipeline...")
        
        # Load embedding model (same as offline)
        if VERBOSE:
            print(f"[ONLINE] Loading embedding model: {EMBEDDING_MODEL_NAME}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        
        # Load FAISS index
        if not os.path.exists(VECTOR_INDEX_FILE):
            raise FileNotFoundError(
                f"FAISS index not found at {VECTOR_INDEX_FILE}. "
                "Please run offline ingestion first."
            )
        
        if VERBOSE:
            print(f"[ONLINE] Loading FAISS index from {VECTOR_INDEX_FILE}")
        self.index = faiss.read_index(VECTOR_INDEX_FILE)
        
        # Load metadata
        if not os.path.exists(METADATA_FILE):
            raise FileNotFoundError(
                f"Metadata not found at {METADATA_FILE}. "
                "Please run offline ingestion first."
            )
        
        if VERBOSE:
            print(f"[ONLINE] Loading metadata from {METADATA_FILE}")
        with open(METADATA_FILE, 'rb') as f:
            self.chunks_metadata = pickle.load(f)
        
        # Initialize tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding(TIKTOKEN_ENCODING)
        
        # Optional: Load cross-encoder for re-ranking (can be resource-intensive)
        # Uncomment if you want more sophisticated re-ranking
        # self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.cross_encoder = None
        
        if VERBOSE:
            print(f"[ONLINE] Loaded {len(self.chunks_metadata)} chunks")
            print("[ONLINE] Retrieval pipeline ready.")
    
    def preprocess_question(self, question: str) -> str:
        """
        Preprocess and normalize the question.
        
        Args:
            question: Raw user question
            
        Returns:
            Preprocessed question
        """
        # Remove extra whitespace
        question = re.sub(r'\s+', ' ', question).strip()
        
        # Optional: Add question mark if missing
        if question and not question.endswith('?'):
            question = question + '?'
        
        return question
    
    def retrieve_initial_candidates(
        self, 
        question: str, 
        k: int = INITIAL_RETRIEVAL_K
    ) -> List[Tuple[int, float]]:
        """
        Retrieve initial candidates using vector similarity.
        
        Args:
            question: Preprocessed question
            k: Number of candidates to retrieve
            
        Returns:
            List of (chunk_index, distance) tuples
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([question])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, k)
        
        # Return list of (index, distance) tuples
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.chunks_metadata):  # Valid index
                results.append((int(idx), float(dist)))
        
        return results
    
    def calculate_keyword_overlap(self, question: str, chunk_text: str) -> float:
        """
        Calculate keyword overlap score between question and chunk.
        
        Args:
            question: User question
            chunk_text: Chunk text
            
        Returns:
            Overlap score (0-1)
        """
        # Normalize and tokenize
        question_words = set(question.lower().split())
        chunk_words = set(chunk_text.lower().split())
        
        # Remove common stop words (simple approach)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
        question_words -= stop_words
        chunk_words -= stop_words
        
        # Calculate Jaccard similarity
        if not question_words or not chunk_words:
            return 0.0
        
        intersection = len(question_words & chunk_words)
        union = len(question_words | chunk_words)
        
        return intersection / union if union > 0 else 0.0
    
    def rerank_candidates(
        self, 
        question: str,
        candidates: List[Tuple[int, float]],
        top_k: int = RERANK_TOP_K
    ) -> List[Dict]:
        """
        Re-rank candidates using hybrid scoring.
        
        Args:
            question: User question
            candidates: List of (chunk_index, distance) from initial retrieval
            top_k: Number of top chunks to return
            
        Returns:
            List of chunk metadata with scores, sorted by relevance
        """
        scored_chunks = []
        
        for chunk_idx, distance in candidates:
            metadata = self.chunks_metadata[chunk_idx]
            chunk_text = metadata['chunk_text']
            
            # Convert L2 distance to similarity (lower distance = higher similarity)
            vector_similarity = 1 / (1 + distance)  # Normalize to 0-1 range
            
            # Calculate keyword overlap
            keyword_score = self.calculate_keyword_overlap(question, chunk_text)
            
            # Hybrid scoring (weighted combination)
            # You can adjust these weights
            final_score = (0.7 * vector_similarity) + (0.3 * keyword_score)
            
            # Only include if above minimum threshold
            if final_score >= RERANK_MIN_SCORE:
                scored_chunks.append({
                    'chunk_index': chunk_idx,
                    'metadata': metadata,
                    'score': final_score,
                    'vector_similarity': vector_similarity,
                    'keyword_score': keyword_score
                })
        
        # Sort by score (descending)
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top k
        return scored_chunks[:top_k]
    
    def construct_context(
        self, 
        ranked_chunks: List[Dict],
        max_tokens: int = MAX_CONTEXT_TOKENS
    ) -> str:
        """
        Construct context from ranked chunks within token budget.
        
        Args:
            ranked_chunks: List of chunks with scores
            max_tokens: Maximum tokens for context
            
        Returns:
            Constructed context string
        """
        context_parts = []
        total_tokens = 0
        
        for i, chunk_data in enumerate(ranked_chunks):
            chunk_text = chunk_data['metadata']['chunk_text']
            chunk_tokens = chunk_data['metadata']['token_count']
            
            # Check if adding this chunk would exceed budget
            if total_tokens + chunk_tokens > max_tokens:
                break
            
            # Add chunk with separator
            context_parts.append(f"[Passage {i+1}]\n{chunk_text}")
            total_tokens += chunk_tokens
        
        # Join all parts
        context = "\n\n".join(context_parts)
        
        return context
    
    def retrieve(
        self, 
        question: str,
        return_metadata: bool = False
    ) -> Dict:
        """
        Complete retrieval pipeline for a question.
        
        Args:
            question: User question
            return_metadata: Whether to return detailed metadata
            
        Returns:
            Dictionary with context and optionally metadata
        """
        if VERBOSE:
            print(f"\n[ONLINE] Processing question: {question}")
        
        # Step 1: Preprocess question
        processed_question = self.preprocess_question(question)
        if VERBOSE:
            print(f"[ONLINE] Preprocessed: {processed_question}")
        
        # Step 2: Initial retrieval
        if VERBOSE:
            print(f"[ONLINE] Retrieving top {INITIAL_RETRIEVAL_K} candidates...")
        candidates = self.retrieve_initial_candidates(processed_question)
        
        # Step 3: Re-rank candidates
        if VERBOSE:
            print(f"[ONLINE] Re-ranking to top {RERANK_TOP_K}...")
        ranked_chunks = self.rerank_candidates(processed_question, candidates)
        
        if not ranked_chunks:
            if VERBOSE:
                print("[ONLINE] No relevant chunks found above threshold.")
            return {
                'context': '',
                'num_chunks': 0,
                'chunks': []
            }
        
        # Step 4: Construct context
        if VERBOSE:
            print(f"[ONLINE] Constructing context from {len(ranked_chunks)} chunks...")
        context = self.construct_context(ranked_chunks)
        
        if VERBOSE:
            context_tokens = len(self.tokenizer.encode(context))
            print(f"[ONLINE] Context size: {context_tokens} tokens")
        
        result = {
            'context': context,
            'num_chunks': len(ranked_chunks),
            'question': processed_question
        }
        
        if return_metadata:
            result['chunks'] = ranked_chunks
        
        return result


def main():
    """Example usage of online retrieval."""
    print("=" * 70)
    print("RAG ONLINE RETRIEVAL - QUERY PROCESSING PHASE")
    print("=" * 70)
    
    # Initialize retrieval pipeline
    retrieval = OnlineRetrieval()
    
    # Test queries
    test_questions = [
        "What are the benefits of RuPay?",
        "How do I apply for a RuPay card?",
        "What is the transaction limit?",
    ]
    
    for question in test_questions:
        print("\n" + "=" * 70)
        result = retrieval.retrieve(question, return_metadata=True)
        
        print(f"\nQuestion: {question}")
        print(f"Chunks retrieved: {result['num_chunks']}")
        
        if result['num_chunks'] > 0:
            print("\nTop chunks:")
            for chunk in result['chunks']:
                print(f"\n  Score: {chunk['score']:.3f} (vector: {chunk['vector_similarity']:.3f}, keyword: {chunk['keyword_score']:.3f})")
                print(f"  Document: {chunk['metadata']['document_id']}")
                print(f"  Preview: {chunk['metadata']['chunk_text'][:150]}...")
            
            print(f"\nConstructed context ({len(result['context'])} chars):")
            print(result['context'][:500] + "..." if len(result['context']) > 500 else result['context'])
        else:
            print("\nNo relevant context found.")


if __name__ == "__main__":
    main()
