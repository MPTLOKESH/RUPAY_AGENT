# Quick Start Guide - Updated RAG System

## ✅ What Changed

The RAG system now uses **your existing LLM endpoint** (no Google API key needed!)

- **Before**: Required Google Gemini API key
- **After**: Uses the same OpenAI-compatible endpoint as your main application

## 🚀 How to Use

### Step 1: Restart the Backend

The backend is currently running with the old RAG agent. You need to restart it:

1. **Stop the current backend**:
   - Go to the terminal running `python backend_api.py`
   - Press `Ctrl + C` to stop it

2. **Start it again**:
   ```bash
   python backend_api.py
   ```

### Step 2: Test Through the UI

Once the backend restarts, you can test RAG queries through your existing UI:

**Example Questions to Try**:
- "What are the benefits of RuPay?"
- "What types of RuPay cards are available?"
- "Tell me about RuPay Platinum cards"

**Expected Behavior**:
- ✅ Questions about RuPay → Answered using ingested documents
- ✅ Out-of-scope questions → "I don't have enough information"
- ✅ Transaction queries → Still work as before

### Step 3: Monitor Backend Logs

Watch the backend output to see RAG in action:

```
[RAGAgent] ✅ RAG Pipeline initialized successfully
[RAGAgent] Loaded 8 chunks from 1 documents
[RAGAgent] Processing query: What are the benefits of RuPay?
[ONLINE] Retrieving top 20 candidates...
[ONLINE] Re-ranking to top 5...
[GENERATION] Generating answer...
[RAGAgent] ✅ Query processed: 4 chunks used, answer length: 245 chars
```

## 📊 System Status

### Offline Phase (✅ Complete)
- Documents ingested: 1 (rupay_document.pdf)
- Chunks created: 8
- Total tokens: 4,220
- Index saved: `data/rupay_faiss.index`

### Online Phase (✅ Ready)
- Embedding model: all-MiniLM-L6-v2
- LLM endpoint: http://183.82.7.228:9532/v1 (same as main app)
- Retrieval: Vector search + Hybrid re-ranking
- Generation: Strict RAG prompting (temp 0.2)

## 🎯 Integration Status

- ✅ Uses existing LLM endpoint (no API key needed)
- ✅ Compatible with current backend
- ✅ No changes to frontend needed
- ✅ Works with existing agent orchestration

## 🔧 Adding More Documents

To add more documents to the knowledge base:

1. Place PDF or TXT files in `data/documents/`
2. Run: `python -m core.offline_ingestion`
3. Restart backend

The RAG system will automatically use the updated index.

## 📝 Configuration

All settings in `core/rag_config.py`:
- Chunk size: 600 tokens (400-800 range)
- Overlap: 15% (~90 tokens)
- Initial retrieval: Top-20
- Re-ranking: Top-5
- Min score threshold: 0.3
- LLM temperature: 0.2

## 🐛 Troubleshooting

### "No relevant chunks found"
- Check if documents are ingested: `python -m core.offline_ingestion`
- Lower threshold in `core/rag_config.py`: `RERANK_MIN_SCORE = 0.2`

### Backend not starting
- Check if ports are free (5000 for backend)
- Verify Docker containers are running
- Check dependencies are installed

### RAG returning errors
- Check backend logs for specific error messages
- Verify LLM endpoint is accessible
- Ensure FAISS index exists: `data/rupay_faiss.index`

---

**Ready to test!** Just restart your backend and try asking RuPay questions through the UI.
