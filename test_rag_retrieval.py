"""
Test script for RAG system - Tests retrieval without requiring LLM API key
"""

from core.offline_ingestion import OfflineIngestion
from core.online_retrieval import OnlineRetrieval
import os

def test_retrieval_only():
    """Test the retrieval pipeline without LLM generation."""
    
    print("=" * 70)
    print("RAG SYSTEM TEST - RETRIEVAL ONLY")
    print("=" * 70)
    
    # Check if index exists
    if not os.path.exists("data/rupay_faiss.index"):
        print("\n⚠️  No index found. Running offline ingestion...")
        ingestion = OfflineIngestion()
        ingestion.ingest_directory("data/documents")
        ingestion.save_index()
        stats = ingestion.get_stats()
        print(f"\n✅ Ingested {stats['total_chunks']} chunks")
    
    # Initialize retrieval
    print("\n" + "=" * 70)
    print("INITIALIZING RETRIEVAL")
    print("=" * 70)
    retrieval = OnlineRetrieval()
    
    # Test queries
    test_questions = [
        "What are the benefits of RuPay?",
        "What types of RuPay cards are available?",
        "How does RuPay work?",
    ]
    
    print("\n" + "=" * 70)
    print("TESTING QUERIES")
    print("=" * 70)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 70}")
        print(f"QUERY {i}")
        print(f"{'=' * 70}")
        print(f"\nQuestion: {question}")
        
        result = retrieval.retrieve(question, return_metadata=True)
        
        print(f"\nChunks retrieved: {result['num_chunks']}")
        
        if result['num_chunks'] > 0:
            print("\nTop retrieved chunks:")
            for j, chunk in enumerate(result['chunks'], 1):
                print(f"\n  [{j}] Score: {chunk['score']:.3f}")
                print(f"      Vector: {chunk['vector_similarity']:.3f}, Keyword: {chunk['keyword_score']:.3f}")
                print(f"      Document: {chunk['metadata']['document_id']}")
                print(f"      Tokens: {chunk['metadata']['token_count']}")
                print(f"      Preview: {chunk['metadata']['chunk_text'][:200]}...")
        else:
            print("\n  No relevant chunks found (below threshold)")
        
        print(f"\nContext constructed: {len(result['context'])} characters")
        if result['context']:
            print(f"\nContext preview:")
            print(result['context'][:400] + "..." if len(result['context']) > 400 else result['context'])
    
    print("\n" + "=" * 70)
    print("✅ RETRIEVAL TEST COMPLETE")
    print("=" * 70)
    print("\nNote: To test full RAG with LLM generation, set GOOGLE_API_KEY")
    print("environment variable and run: python -m core.rag_pipeline")

if __name__ == "__main__":
    test_retrieval_only()
