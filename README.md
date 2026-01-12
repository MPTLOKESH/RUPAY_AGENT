# RuPay AI Agent - Complete Guide

## Overview

This is a **RuPay AI Agent** built with **FastAPI** (backend) and **React** (frontend) that helps users with:
- Transaction status queries
- General RuPay card information (using RAG system)
- Banking assistance

## Quick Start

### 1. Start Docker Containers
```bash
docker-compose up -d
```
This starts PostgreSQL and Redis.

### 2. Start Backend
```bash
python backend_api.py
```
Backend runs on **http://localhost:5000**

### 3. Start Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on **http://localhost:3000**

### 4. Open Browser
Visit **http://localhost:3000** and start chatting!

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   FastAPI    │────────▶│  PostgreSQL │
│   (React)   │         │   Backend    │         │  (Docker)   │
└─────────────┘         └──────────────┘         └─────────────┘
                              │                         
                              ├──────────▶ Redis (Chat History)
                              │
                              └──────────▶ RAG System (Document Q&A)
```

## Core Components

### Backend (`backend_api.py`)
- **FastAPI** server handling API requests
- Routes:
  - `POST /api/chat` - Main chat endpoint
  - `GET /api/history/{session_id}` - Get chat history
  - `DELETE /api/history/{session_id}` - Clear history
  - `GET /api/database` - Get recent transactions

### Main Orchestrator (`main_orchestraion.py`)
Routes user queries to the appropriate agent:
- **Transaction Agent** - SQL database queries for transactions
- **RAG Agent** - Document-based Q&A about RuPay
- **Identity Agent** - Greetings and basic info
- **Guardrail Agent** - Blocks inappropriate content

### Agents

#### 1. Transaction Agent (`agents/agent_transaction.py`)
- Queries PostgreSQL for transaction data
- Analyzes failed transactions
- Returns user-friendly explanations

#### 2. RAG Agent (`agents/agent_rag.py`)
- Uses the RAG pipeline for document Q&A
- Answers questions about RuPay cards, features, limits, etc.
- See `RAG_ARCHITECTURE.md` for detailed RAG documentation

### Database
- **PostgreSQL** (port 5432) - Stores transaction data
- **Redis** (port 6379) - Stores chat session history

### Frontend (`frontend/`)
- **React** with Vite
- Modern chat interface with:
  - Session management
  - Dark mode
  - RuPay branding
  - Loading animations

## RAG System

The **Retrieval-Augmented Generation (RAG)** system powers document-based Q&A.

**For complete RAG documentation, see:** [`RAG_ARCHITECTURE.md`](RAG_ARCHITECTURE.md)

### Quick RAG Overview
- **Offline Phase**: Documents are chunked (400-800 tokens) and embedded
- **Online Phase**: User queries retrieve relevant chunks → LLM generates answers
- **Key Features**: 
  - Token-based chunking with 15% overlap
  - Hybrid re-ranking (vector + keyword)
  - Strict context-only prompting (prevents hallucination)

### Adding Documents to RAG
```bash
# Place PDFs in data/documents/
python -m core.offline_ingestion

# Restart backend
python backend_api.py
```

## Configuration

### LLM Endpoint
Edit `main_orchestraion.py`:
```python
MODEL_URL = "http://your-llm-endpoint/v1"
```

### Database
Edit `docker-compose.yml` for DB credentials.

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5000
taskkill /F /PID <process_id>

# Then restart
python backend_api.py
```

### Docker Containers Not Running
```bash
docker-compose up -d
docker ps  # verify running
```

### RAG Not Working
- Ensure documents are ingested: `python -m core.offline_ingestion`
- Check `data/rupay_faiss.index` exists
- Restart backend

### HuggingFace Timeout
The system now uses cached models (`local_files_only=True`), so downloads shouldn't occur after first run.

## File Structure

```
Rupay_agent/
├── backend_api.py           # Main FastAPI server
├── main_orchestraion.py     # Agent orchestration logic
├── docker-compose.yml       # Docker services config
├── RAG_ARCHITECTURE.md      # Complete RAG documentation
│
├── agents/                  # Agent implementations
│   ├── agent_transaction.py
│   └── agent_rag.py
│
├── core/                    # Core utilities
│   ├── rag_pipeline.py      # RAG orchestrator
│   ├── offline_ingestion.py # Document ingestion
│   ├── online_retrieval.py  # Query retrieval
│   ├── rag_generation.py    # LLM answer generation
│   └── rag_config.py        # RAG configuration
│
├── data/                    # Data files
│   ├── documents/           # PDFs for RAG
│   ├── rupay_faiss.index    # Vector index
│   └── rupay_metadata.pkl   # Chunk metadata
│
└── frontend/                # React application
    └── src/
        └── App.jsx          # Main UI
```

## Development Tips

### Testing RAG Standalone
```bash
python -m core.rag_pipeline
```

### Testing Retrieval Only
```bash
python -m core.online_retrieval
```

### API Documentation
Visit **http://localhost:5000/docs** when backend is running for interactive API docs (Swagger UI).

## Technologies Used

- **Backend**: FastAPI, Python 3.14
- **Frontend**: React, Vite
- **Database**: PostgreSQL, Redis (Docker)
- **LLM**: Custom OpenAI-compatible endpoint
- **RAG**: 
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
  - Vector DB: FAISS
  - Chunking: tiktoken (token-based)
  - LLM: Custom endpoint via LangChain

## Support

For RAG-specific questions, see **[RAG_ARCHITECTURE.md](RAG_ARCHITECTURE.md)**

---

**Last Updated**: 2026-01-12
