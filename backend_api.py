from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import create_engine
from main_orchestraion import MainOrchestrator, DB_CONFIG
from core.redis_client import save_message, get_history as get_redis_history, clear_history
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="RuPay AI Agent API",
    description="AI-powered transaction assistant API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the AI agent
orchestrator = MainOrchestrator()

# Database connection URL
db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str
    session_id: str = None
    history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    response: str

class DatabaseResponse(BaseModel):
    data: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    status: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat messages from the frontend
    
    - **message**: User's message to the AI agent
    - **session_id**: Unique session ID for persistent history
    - **history**: Previous conversation history (optional, used if session_id not provided)
    """
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Determine history source
        conversation_history = request.history
        if request.session_id:
            # Fetch history from Redis
            redis_history = get_redis_history(request.session_id)
            if redis_history:
                conversation_history = redis_history
        
        # Get response from the orchestrator
        # Note: orchestrator expects history of previous turns
        response = orchestrator.chat(request.message, conversation_history)
        
        # Save to Redis if session_id is active
        if request.session_id:
            save_message(request.session_id, "user", request.message)
            save_message(request.session_id, "assistant", response)
        
        return ChatResponse(response=response)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{session_id}", response_model=List[Dict[str, str]])
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a specific session
    """
    try:
        return get_redis_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Clear chat history for a specific session
    """
    try:
        clear_history(session_id)
        return {"status": "success", "message": "History cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/database", response_model=DatabaseResponse)
async def get_database():
    """
    Fetch recent transactions from the database
    
    Returns the last 15 transactions ordered by date and time
    """
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Fetch last 15 transactions
            query = "SELECT * FROM transactions ORDER BY tstamp_trans DESC LIMIT 15"
            df = pd.read_sql(query, conn)
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Convert datetime objects to strings and map keys for frontend
        for record in data:
            if 'tstamp_trans' in record:
                record['date_and_time'] = str(record['tstamp_trans'])
            
            if 'amt' in record:
                record['amount'] = record['amt']
                
        return DatabaseResponse(data=data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint
    
    Returns the API status
    """
    return HealthResponse(status="healthy")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "RuPay AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == '__main__':
    print("🚀 Starting RuPay AI Agent Backend API (FastAPI)...")
    print("📡 API will be available at: http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/docs")
    print("🔗 Frontend should connect to: http://localhost:3000")
    print("\n✨ FastAPI features enabled:")
    print("   - Automatic API documentation (Swagger UI)")
    print("   - Request/response validation")
    print("   - Async support for better performance")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
