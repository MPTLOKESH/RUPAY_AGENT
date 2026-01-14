"""
RAG System Configuration
Centralized configuration for all RAG components
"""

import os

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================
# Token-based chunking parameters
MIN_CHUNK_SIZE = 400  # Minimum tokens per chunk
MAX_CHUNK_SIZE = 800  # Maximum tokens per chunk
DEFAULT_CHUNK_SIZE = 600  # Default chunk size in tokens
CHUNK_OVERLAP_PERCENTAGE = 15  # 15% overlap between chunks
CHUNK_OVERLAP = int(DEFAULT_CHUNK_SIZE * CHUNK_OVERLAP_PERCENTAGE / 100)  # ~90 tokens

# Tiktoken encoding model
TIKTOKEN_ENCODING = "cl100k_base"  # GPT-3.5/4 encoding

# ============================================================================
# STORAGE PATHS
# ============================================================================
DATA_DIR = "data"
VECTOR_INDEX_FILE = os.path.join(DATA_DIR, "rupay_faiss.index")
METADATA_FILE = os.path.join(DATA_DIR, "rupay_metadata.pkl")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# ============================================================================
# RETRIEVAL CONFIGURATION
# ============================================================================
# Initial retrieval parameters
INITIAL_RETRIEVAL_K = 20  # Retrieve top-20 candidates for re-ranking

# Re-ranking parameters
RERANK_TOP_K = 5  # Final number of chunks after re-ranking
RERANK_MIN_SCORE = 0.3  # Minimum similarity score threshold

# ============================================================================
# LLM GENERATION CONFIGURATION
# ============================================================================
# Generation parameters
LLM_TEMPERATURE = 0.2  # Low temperature for deterministic answers
LLM_MAX_TOKENS = 1000  # Maximum tokens in generated response

# Context construction
MAX_CONTEXT_TOKENS = 3000  # Maximum tokens to send to LLM as context

# System prompt template (strict - for RuPay-specific queries)
SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant that answers questions ONLY using the provided context.

RULES:
1. Only use information from the context below
2. If the answer is not in the context, respond: "I don't have enough information to answer this question."
3. Do not use external knowledge or make assumptions
4. Keep answers concise and factual
5. Quote relevant parts of the context when appropriate
6. **FORMATTING**: Use Markdown for headers, lists, and bold text. Do NOT use HTML tags.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""

# NPCI domain prompt template (flexible - allows external knowledge for NPCI topics)
NPCI_PROMPT_TEMPLATE = """You are a knowledgeable assistant specializing in NPCI (National Payments Corporation of India) and payment systems.

CONTEXT FROM DOCUMENTS:
{context}

If the context provides relevant information, use it. However, if the context is insufficient or empty, you may use your general knowledge about NPCI, FASTag, UPI infrastructure, payment systems, and related topics to provide a helpful answer.

Keep answers concise, accurate, and factual.
**FORMATTING**: Use Markdown for headers, lists, and bold text. Do NOT use HTML tags.

QUESTION:
{question}

ANSWER:"""

# Fallback response when no relevant context is found
NO_CONTEXT_RESPONSE = "I don't have enough information to answer this question."

# NPCI-related keywords for flexible prompting
NPCI_KEYWORDS = ['npci', 'fastag', 'upi infrastructure', 'nach system', 'imps network', 'payment ecosystem', 'nfs', 'aeps', 'bharat billpay']

# ============================================================================
# OFFLINE INGESTION CONFIGURATION
# ============================================================================
# Supported file formats
SUPPORTED_FORMATS = [".pdf", ".txt"]

# Text cleaning parameters
REMOVE_EXTRA_WHITESPACE = True
NORMALIZE_UNICODE = True
MIN_CHUNK_LENGTH = 50  # Minimum characters for a valid chunk

# ============================================================================
# LOGGING AND DEBUG
# ============================================================================
VERBOSE = True  # Print detailed logs
DEBUG_MODE = False  # Additional debug information
