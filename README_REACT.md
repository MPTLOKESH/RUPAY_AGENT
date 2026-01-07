# RuPay Transaction Assistant - React Frontend

A modern, professional React frontend for the RuPay AI Agent with a beautiful UI featuring glassmorphism effects, smooth animations, and a responsive design.

## 🎨 Features

- **Modern UI Design**: Dark theme with vibrant gradients and glassmorphism effects
- **Real-time Chat Interface**: Interactive chat with the AI agent
- **Database Viewer**: Live view of recent transactions from PostgreSQL
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Smooth Animations**: Professional transitions and micro-interactions

## 📁 Project Structure

```
frontend/
├── index.html              # HTML entry point
├── package.json            # Dependencies
├── vite.config.js          # Vite configuration
└── src/
    ├── main.jsx            # React entry point
    ├── App.jsx             # Main application component
    ├── App.css             # Global styles
    ├── components/
    │   ├── Header.jsx      # Header component
    │   ├── ChatMessage.jsx # Message display component
    │   ├── ChatInput.jsx   # Input component
    │   └── DatabaseViewer.jsx # Database sidebar
    └── services/
        └── api.js          # API service layer
```

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Python backend running on port 5000

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_api.txt
   ```

2. **Start the backend API:**
   ```bash
   python backend_api.py
   ```

   The API will be available at `http://localhost:5000`

## 🔧 Configuration

The frontend is configured to proxy API requests to `http://localhost:5000`. This is set in `vite.config.js`:

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

## 📡 API Endpoints

The backend provides the following endpoints:

- `POST /api/chat` - Send a message to the AI agent
  - Body: `{ "message": "string", "history": [] }`
  - Response: `{ "response": "string" }`

- `GET /api/database` - Fetch recent transactions
  - Response: `{ "data": [...] }`

- `GET /api/health` - Health check
  - Response: `{ "status": "healthy" }`

## 🎯 Usage

1. **Start both servers:**
   - Backend: `python backend_api.py` (port 5000)
   - Frontend: `npm run dev` (port 3000)

2. **Open your browser:**
   - Navigate to `http://localhost:3000`

3. **Interact with the agent:**
   - Type your question in the chat input
   - Click "Refresh" in the database viewer to see recent transactions
   - Copy transaction details from the database to test queries

## 🎨 Design System

The application uses a modern design system with:

- **Color Palette**: Dark theme with purple/blue gradients
- **Typography**: Inter font family from Google Fonts
- **Spacing**: Consistent 8px grid system
- **Animations**: Smooth transitions with cubic-bezier easing
- **Effects**: Glassmorphism, shadows, and hover states

## 📱 Responsive Breakpoints

- Desktop: > 1024px
- Tablet: 640px - 1024px
- Mobile: < 640px

## 🛠️ Build for Production

```bash
cd frontend
npm run build
```

The production build will be in the `dist/` folder.

## 🐛 Troubleshooting

**Frontend not connecting to backend:**
- Ensure backend is running on port 5000
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.js`

**Database viewer not loading:**
- Ensure PostgreSQL is running
- Check database credentials in `main_orchestraion.py`
- Verify Docker container is running (if using Docker)

**npm not found:**
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation

## 📄 License

This project is part of the RuPay AI Agent system.
