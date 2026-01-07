# Quick Start Guide - RuPay AI Agent

## 🚀 How to Run (2 Simple Steps)

### Step 1: Start Backend (Terminal 1)
```bash
pip install -r requirements_api.txt
python backend_api.py
```

### Step 2: Start Frontend (Terminal 2)
```bash
cd frontend
npm install
npm run dev
```

### Step 3: Open Browser
Navigate to: **http://localhost:3000**

---

## 📚 API Documentation
Once backend is running, visit: **http://localhost:5000/docs**

---

## ✅ What Changed to FastAPI

- ✨ **Automatic API Documentation** at `/docs` and `/redoc`
- ✨ **Request/Response Validation** with Pydantic models
- ✨ **Async Support** for better performance
- ✨ **Type Safety** with Python type hints
- ✨ **Better Error Messages** with detailed validation errors

---

## 🔧 Commands Reference

### Backend
```bash
# Install dependencies
pip install -r requirements_api.txt

# Run backend
python backend_api.py

# Run with auto-reload (for development)
uvicorn backend_api:app --reload --port 5000
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Docs (Swagger)**: http://localhost:5000/docs
- **API Docs (ReDoc)**: http://localhost:5000/redoc
- **Health Check**: http://localhost:5000/api/health

---

## 💡 Tips

1. **Always start backend first**, then frontend
2. **Keep both terminals open** while using the app
3. **Visit `/docs`** to test API endpoints directly
4. **Press Ctrl+C** in each terminal to stop the servers

For detailed instructions, see [RUN_INSTRUCTIONS.md](file:///c:/Users/admin/Downloads/llm_code_rupay/llm_code/llm_code/RUN_INSTRUCTIONS.md)
