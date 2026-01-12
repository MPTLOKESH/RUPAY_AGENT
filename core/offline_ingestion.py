"""
OFFLINE INGESTION MODULE
Handles the complete offline knowledge preparation pipeline:
1. Load documents (PDF, TXT)
2. Clean and normalize text
3. Token-based chunking (400-800 tokens, 15% overlap)
4. Generate embeddings
5. Store in FAISS vector database
"""

import os
import re
import pickle
import numpy as np
from typing import List, Dict, Tuple
import tiktoken
from sentence_transformers import SentenceTransformer
import faiss
from pypdf import PdfReader

# Import configuration
from core.rag_config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    DEFAULT_CHUNK_SIZE,
    CHUNK_OVERLAP,
    TIKTOKEN_ENCODING,
    VECTOR_INDEX_FILE,
    METADATA_FILE,
    SUPPORTED_FORMATS,
    MIN_CHUNK_LENGTH,
    VERBOSE,
    DOCUMENTS_DIR
)


class OfflineIngestion:
    """
    Handles offline document ingestion and vector database creation.
    This should be run once or whenever documents are updated.
    """
    
    def __init__(self):
        """Initialize the ingestion pipeline."""
        if VERBOSE:
            print("[OFFLINE] Initializing Ingestion Pipeline...")
        
        # Load embedding model
        if VERBOSE:
            print(f"[OFFLINE] Loading embedding model: {EMBEDDING_MODEL_NAME}")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        
        # Initialize tiktoken encoder for token-based chunking
        self.tokenizer = tiktoken.get_encoding(TIKTOKEN_ENCODING)
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
        
        # Storage for chunk metadata
        self.chunks_metadata = []  # List of dicts with chunk info
        
        if VERBOSE:
            print("[OFFLINE] Ingestion pipeline ready.")
    
    def load_text_file(self, file_path: str) -> str:
        """Load text from a .txt file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_pdf_file(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        reader = PdfReader(file_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    
    def load_document(self, file_path: str) -> str:
        """
        Load a document based on file extension.
        
        Args:
            file_path: Path to the document
            
        Returns:
            Extracted text content
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {SUPPORTED_FORMATS}")
        
        if VERBOSE:
            print(f"[OFFLINE] Loading document: {file_path}")
        
        if ext == ".pdf":
            return self.load_pdf_file(file_path)
        elif ext == ".txt":
            return self.load_text_file(file_path)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
        
        # Normalize unicode
        text = text.strip()
        
        return text
    
    def chunk_by_tokens(
        self, 
        text: str, 
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP
    ) -> List[str]:
        """
        Split text into chunks based on token count with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target size in tokens (default 600)
            overlap: Overlap in tokens (default ~90)
            
        Returns:
            List of text chunks
        """
        # Encode text into tokens
        tokens = self.tokenizer.encode(text)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            # Get chunk of tokens
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            # Only add chunks that meet minimum length
            if len(chunk_text) >= MIN_CHUNK_LENGTH:
                chunks.append(chunk_text)
            
            # Move start position with overlap
            start += chunk_size - overlap
        
        return chunks
    
    def generate_embeddings(self, chunks: List[str]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Numpy array of embeddings
        """
        if VERBOSE:
            print(f"[OFFLINE] Generating embeddings for {len(chunks)} chunks...")
        
        embeddings = self.embedding_model.encode(
            chunks,
            show_progress_bar=VERBOSE,
            convert_to_numpy=True
        )
        
        return embeddings.astype('float32')
    
    def ingest_document(
        self, 
        file_path: str,
        document_id: str = None
    ) -> Dict:
        """
        Complete ingestion pipeline for a single document.
        
        Args:
            file_path: Path to document
            document_id: Optional identifier for the document
            
        Returns:
            Stats about ingestion
        """
        if document_id is None:
            document_id = os.path.basename(file_path)
        
        # Step 1: Load document
        raw_text = self.load_document(file_path)
        
        # Step 2: Clean text
        if VERBOSE:
            print(f"[OFFLINE] Cleaning text...")
        cleaned_text = self.clean_text(raw_text)
        
        # Step 3: Chunk by tokens
        if VERBOSE:
            print(f"[OFFLINE] Chunking text (size={DEFAULT_CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        chunks = self.chunk_by_tokens(cleaned_text)
        
        if VERBOSE:
            print(f"[OFFLINE] Created {len(chunks)} chunks")
        
        # Step 4: Generate embeddings
        embeddings = self.generate_embeddings(chunks)
        
        # Step 5: Add to FAISS index
        if VERBOSE:
            print(f"[OFFLINE] Adding to FAISS index...")
        self.index.add(embeddings)
        
        # Step 6: Store metadata
        for i, chunk in enumerate(chunks):
            metadata = {
                'document_id': document_id,
                'chunk_index': i,
                'chunk_text': chunk,
                'token_count': len(self.tokenizer.encode(chunk)),
                'char_count': len(chunk)
            }
            self.chunks_metadata.append(metadata)
        
        return {
            'document_id': document_id,
            'num_chunks': len(chunks),
            'total_tokens': sum(m['token_count'] for m in self.chunks_metadata[-len(chunks):]),
            'avg_chunk_tokens': np.mean([m['token_count'] for m in self.chunks_metadata[-len(chunks):]])
        }
    
    def ingest_directory(self, directory_path: str) -> List[Dict]:
        """
        Ingest all supported documents in a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of ingestion stats for each document
        """
        stats = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in SUPPORTED_FORMATS and os.path.isfile(file_path):
                try:
                    doc_stats = self.ingest_document(file_path)
                    stats.append(doc_stats)
                except Exception as e:
                    print(f"[OFFLINE] Error ingesting {filename}: {e}")
        
        return stats
    
    def save_index(self):
        """Save FAISS index and metadata to disk."""
        if VERBOSE:
            print(f"[OFFLINE] Saving FAISS index to {VECTOR_INDEX_FILE}...")
        faiss.write_index(self.index, VECTOR_INDEX_FILE)
        
        if VERBOSE:
            print(f"[OFFLINE] Saving metadata to {METADATA_FILE}...")
        with open(METADATA_FILE, 'wb') as f:
            pickle.dump(self.chunks_metadata, f)
        
        if VERBOSE:
            print(f"[OFFLINE] Successfully saved {len(self.chunks_metadata)} chunks")
    
    def get_stats(self) -> Dict:
        """Get statistics about the ingested corpus."""
        if not self.chunks_metadata:
            return {"total_chunks": 0}
        
        token_counts = [m['token_count'] for m in self.chunks_metadata]
        
        return {
            'total_chunks': len(self.chunks_metadata),
            'total_documents': len(set(m['document_id'] for m in self.chunks_metadata)),
            'avg_chunk_tokens': np.mean(token_counts),
            'min_chunk_tokens': np.min(token_counts),
            'max_chunk_tokens': np.max(token_counts),
            'total_tokens': np.sum(token_counts)
        }


def main():
    """Example usage of offline ingestion."""
    print("=" * 70)
    print("RAG OFFLINE INGESTION - KNOWLEDGE PREPARATION PHASE")
    print("=" * 70)
    
    # Initialize ingestion pipeline
    ingestion = OfflineIngestion()
    
    # Ingest documents from the documents directory
    print(f"\nIngesting documents from: {DOCUMENTS_DIR}")
    stats = ingestion.ingest_directory(DOCUMENTS_DIR)
    
    # Display stats for each document
    print("\n" + "=" * 70)
    print("INGESTION RESULTS")
    print("=" * 70)
    for stat in stats:
        print(f"\nDocument: {stat['document_id']}")
        print(f"  - Chunks created: {stat['num_chunks']}")
        print(f"  - Total tokens: {stat['total_tokens']:.0f}")
        print(f"  - Avg tokens/chunk: {stat['avg_chunk_tokens']:.0f}")
    
    # Save index
    ingestion.save_index()
    
    # Display overall stats
    overall_stats = ingestion.get_stats()
    print("\n" + "=" * 70)
    print("OVERALL STATISTICS")
    print("=" * 70)
    print(f"Total documents: {overall_stats['total_documents']}")
    print(f"Total chunks: {overall_stats['total_chunks']}")
    print(f"Total tokens: {overall_stats['total_tokens']:.0f}")
    print(f"Avg tokens/chunk: {overall_stats['avg_chunk_tokens']:.0f}")
    print(f"Min tokens/chunk: {overall_stats['min_chunk_tokens']:.0f}")
    print(f"Max tokens/chunk: {overall_stats['max_chunk_tokens']:.0f}")
    
    print("\n✅ Offline ingestion complete!")


if __name__ == "__main__":
    main()
