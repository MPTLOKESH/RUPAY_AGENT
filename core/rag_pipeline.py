"""
RAG PIPELINE ORCHESTRATOR
Main entry point that coordinates all RAG phases:
- Offline Phase: Document ingestion and indexing
- Online Phase: Query processing and answer generation

This module provides a unified interface for the complete RAG system.
"""

import os
from typing import Dict, Optional, List

# Import all RAG modules
from core.offline_ingestion import OfflineIngestion
from core.online_retrieval import OnlineRetrieval
from core.rag_generation import RAGGeneration
from core.rag_config import (
    VECTOR_INDEX_FILE,
    METADATA_FILE,
    VERBOSE,
    DOCUMENTS_DIR
)


class RupayRAG:
    """
    Main RAG Pipeline Orchestrator.
    Provides a clean interface for both offline and online operations.
    """
    
    def __init__(self, model_url: Optional[str] = None):
        """
        Initialize the RAG pipeline.
        
        Args:
            model_url: Optional custom LLM endpoint URL
        """
        if VERBOSE:
            print("\n" + "=" * 70)
            print("INITIALIZING RUPAY RAG SYSTEM")
            print("=" * 70)
        
        self.model_url = model_url
        
        # Check if offline phase has been completed
        self.is_offline_ready = os.path.exists(VECTOR_INDEX_FILE) and os.path.exists(METADATA_FILE)
        
        if self.is_offline_ready:
            if VERBOSE:
                print("✅ Offline phase completed - index and metadata found")
            
            # Initialize online components
            self.retrieval = OnlineRetrieval()
            self.generation = RAGGeneration(model_url=model_url)
            
            if VERBOSE:
                print("✅ Online components initialized")
        else:
            if VERBOSE:
                print("⚠️  Offline phase not completed - run offline ingestion first")
            
            self.retrieval = None
            self.generation = None
    
    # =========================================================================
    # OFFLINE PHASE METHODS
    # =========================================================================
    
    def run_offline_ingestion(
        self, 
        document_paths: Optional[List[str]] = None,
        directory_path: Optional[str] = None
    ) -> Dict:
        """
        Run the complete offline ingestion pipeline.
        
        Args:
            document_paths: List of specific document paths to ingest
            directory_path: Directory containing documents to ingest
            
        Returns:
            Ingestion statistics
        """
        if VERBOSE:
            print("\n" + "=" * 70)
            print("STARTING OFFLINE INGESTION PHASE")
            print("=" * 70)
        
        # Initialize ingestion pipeline
        ingestion = OfflineIngestion()
        
        stats = []
        
        # Ingest from directory
        if directory_path:
            dir_stats = ingestion.ingest_directory(directory_path)
            stats.extend(dir_stats)
        elif not document_paths:
            # Default to DOCUMENTS_DIR
            dir_stats = ingestion.ingest_directory(DOCUMENTS_DIR)
            stats.extend(dir_stats)
        
        # Ingest specific documents
        if document_paths:
            for doc_path in document_paths:
                try:
                    doc_stats = ingestion.ingest_document(doc_path)
                    stats.append(doc_stats)
                except Exception as e:
                    print(f"Error ingesting {doc_path}: {e}")
        
        # Save index
        ingestion.save_index()
        
        # Get overall stats
        overall_stats = ingestion.get_stats()
        
        if VERBOSE:
            print("\n" + "=" * 70)
            print("OFFLINE INGESTION COMPLETE")
            print("=" * 70)
            print(f"Total documents: {overall_stats['total_documents']}")
            print(f"Total chunks: {overall_stats['total_chunks']}")
            print(f"Total tokens: {overall_stats['total_tokens']:.0f}")
            print(f"Avg tokens/chunk: {overall_stats['avg_chunk_tokens']:.0f}")
        
        # Re-initialize online components
        self.is_offline_ready = True
        self.retrieval = OnlineRetrieval()
        self.generation = RAGGeneration(model_url=self.model_url)
        
        return overall_stats
    
    # =========================================================================
    # ONLINE PHASE METHODS
    # =========================================================================
    
    def query(
        self, 
        question: str,
        return_context: bool = False,
        return_metadata: bool = False
    ) -> Dict:
        """
        Process a question through the complete online RAG pipeline.
        
        Args:
            question: User question
            return_context: Whether to return the retrieved context
            return_metadata: Whether to return detailed retrieval metadata
            
        Returns:
            Dictionary with answer and optional metadata
            
        Format (compatible with old ChromaDB implementation):
            {'documents': [[chunk1, chunk2, ...]], 'answer': '...'}
        """
        if not self.is_offline_ready:
            return {
                'documents': [[]],
                'answer': "RAG system not initialized. Please run offline ingestion first."
            }
        
        if VERBOSE:
            print("\n" + "=" * 70)
            print("PROCESSING QUERY")
            print("=" * 70)
        
        # Step 1: Retrieve relevant context
        retrieval_result = self.retrieval.retrieve(
            question, 
            return_metadata=return_metadata
        )
        
        context = retrieval_result['context']
        
        # Step 2: Generate answer
        generation_result = self.generation.generate_answer(
            question, 
            context
        )
        
        answer = generation_result['answer']
        
        # Prepare result
        result = {
            'answer': answer,
            'has_context': generation_result['has_context'],
            'num_chunks': retrieval_result['num_chunks']
        }
        
        # Add context if requested
        if return_context:
            result['context'] = context
        
        # Add metadata if requested
        if return_metadata and 'chunks' in retrieval_result:
            result['chunks'] = retrieval_result['chunks']
        
        # Add documents in old format for backward compatibility
        if retrieval_result['num_chunks'] > 0 and 'chunks' in retrieval_result:
            documents = [chunk['metadata']['chunk_text'] for chunk in retrieval_result['chunks']]
        else:
            documents = []
        
        result['documents'] = [documents]  # Wrap in list for ChromaDB format compatibility
        
        if VERBOSE:
            print(f"\n✅ Query processed successfully")
            print(f"   Chunks used: {result['num_chunks']}")
            print(f"   Answer length: {len(answer)} chars")
        
        return result
    
    def get_system_info(self) -> Dict:
        """Get information about the RAG system status."""
        info = {
            'offline_ready': self.is_offline_ready,
            'index_exists': os.path.exists(VECTOR_INDEX_FILE),
            'metadata_exists': os.path.exists(METADATA_FILE)
        }
        
        if self.is_offline_ready and self.retrieval:
            info['num_chunks'] = len(self.retrieval.chunks_metadata)
            
            documents = set(chunk['document_id'] for chunk in self.retrieval.chunks_metadata)
            info['num_documents'] = len(documents)
            info['documents'] = list(documents)
        
        return info


def main():
    """Example usage of the complete RAG pipeline."""
    print("=" * 70)
    print("RUPAY RAG PIPELINE - COMPLETE DEMONSTRATION")
    print("=" * 70)
    
    # Initialize RAG system
    rag = RupayRAG()
    
    # Check if offline phase is needed
    system_info = rag.get_system_info()
    
    if not system_info['offline_ready']:
        print("\n⚠️  Offline phase not completed. Running ingestion...")
        rag.run_offline_ingestion()
    else:
        print(f"\n✅ System ready with {system_info['num_chunks']} chunks from {system_info['num_documents']} documents")
    
    # Test queries
    print("\n" + "=" * 70)
    print("TESTING QUERIES")
    print("=" * 70)
    
    test_questions = [
        "What are the benefits of RuPay?",
        "How do I apply for a RuPay card?",
        "What is completely unrelated to RuPay?",  # Should return no context response
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {question}")
        
        result = rag.query(question, return_context=False, return_metadata=False)
        
        print(f"A: {result['answer']}")
        print(f"Chunks used: {result['num_chunks']}")


if __name__ == "__main__":
    main()
