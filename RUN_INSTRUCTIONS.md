# 🚀 How to Run the RuPay AI Agent

This guide will help you run the React frontend with the FastAPI backend.

## Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** installed (download from https://nodejs.org/)
- **PostgreSQL database** running (via Docker or local installation)

---

## Step 1: Install Backend Dependencies

Open a terminal in the project directory:

```bash
# Install the API dependencies
pip install -r requirements_api.txt
```

This installs:
- `fastapi` - Modern Python web framework
- `uvicorn` - ASGI server for FastAPI
- `pydantic` - Data validation
- `pandas` - Data manipulation
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL adapter

---

## Step 2: Install Frontend Dependencies

Open a terminal and navigate to the frontend folder:

```bash
cd frontend
npm install
```

This installs React, Vite, Axios, and other frontend dependencies.

---

## Step 3: Start the FastAPI Backend

In the main project directory, run:

```bash
python backend_api.py
```

You should see:
```
🚀 Starting RuPay AI Agent Backend API (FastAPI)...
📡 API will be available at: http://localhost:5000
📚 API Documentation: http://localhost:5000/docs
🔗 Frontend should connect to: http://localhost:3000

✨ FastAPI features enabled:
   - Automatic API documentation (Swagger UI)
   - Request/response validation
   - Async support for better performance

INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**Keep this terminal open!** The backend needs to stay running.

### 🎯 Test the Backend

Open your browser and visit:
- **API Docs**: http://localhost:5000/docs (Interactive Swagger UI)
- **Health Check**: http://localhost:5000/api/health

---

## Step 4: Start the React Frontend

Open a **NEW terminal** (keep the backend running in the first one):

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h to show help
```

---

## Step 5: Open the Application

Open your browser and navigate to:

**http://localhost:3000**

You should see the RuPay Transaction Assistant interface!

---

## 🎨 What You'll See

1. **Header**: Purple gradient banner with "RuPay Transaction Assistant"
2. **Chat Interface**: Main area for chatting with the AI agent
3. **Database Viewer**: Right sidebar with a "Refresh" button to view transactions
4. **Input Field**: At the bottom to type your questions

---

## 💬 Try These Examples

1. Click **"Refresh"** in the database viewer to load transactions
2. Type in the chat: `"Check failed withdrawal of 1500 rs"`
3. Ask: `"What are the transaction limits?"`
4. Copy a date and amount from the database table and ask about it

---

## 🛑 How to Stop

1. **Stop Frontend**: Press `Ctrl+C` in the frontend terminal
2. **Stop Backend**: Press `Ctrl+C` in the backend terminal

---

## 🐛 Troubleshooting

### Issue: "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/ and restart your terminal

### Issue: "Module not found" errors in Python
**Solution**: Make sure you're in the correct directory and run:
```bash
pip install -r requirements.txt
pip install -r requirements_api.txt
```

### Issue: Frontend can't connect to backend
**Solution**: 
- Ensure backend is running on port 5000
- Check that you see "Uvicorn running on http://0.0.0.0:5000"
- Try visiting http://localhost:5000/docs to verify

### Issue: Database viewer shows error
**Solution**:
- Ensure PostgreSQL is running
- Check database credentials in `main_orchestraion.py`
- If using Docker, ensure the container is running:
  ```bash
  docker-compose up -d
  ```

### Issue: Port already in use
**Solution**:
- Backend (port 5000): Change the port in `backend_api.py` (last line)
- Frontend (port 3000): Change the port in `vite.config.js`

---

## 📚 FastAPI Features

### Interactive API Documentation

Visit **http://localhost:5000/docs** to see:
- All available endpoints
- Request/response schemas
- Try out API calls directly in the browser
- Automatic validation documentation

### Alternative API Docs

Visit **http://localhost:5000/redoc** for ReDoc-style documentation

---

## 🔄 Development Workflow

### Making Changes to Frontend
- Edit files in `frontend/src/`
- Vite will automatically reload the page
- No need to restart the server

### Making Changes to Backend
- Edit `backend_api.py`
- Stop the backend (Ctrl+C)
- Restart: `python backend_api.py`
- Or use auto-reload: `uvicorn backend_api:app --reload --port 5000`

---

## 📦 Production Deployment

### Build Frontend
```bash
cd frontend
npm run build
```
The production files will be in `frontend/dist/`

### Run Backend in Production
```bash
uvicorn backend_api:app --host 0.0.0.0 --port 5000 --workers 4
```

---

## ✅ Quick Start Summary

```bash
# Terminal 1 - Backend
pip install -r requirements_api.txt
python backend_api.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev

# Open browser: http://localhost:3000
```

That's it! You're ready to use the RuPay AI Agent! 🎉
