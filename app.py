import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import time

# --- 1. PAGE CONFIG (Must be first) ---
st.set_page_config(page_title="RuPay AI Agent", page_icon="🏦", layout="wide")

# --- 2. IMPORT AGENT ---
# We wrap this in try-except to handle import errors gracefully
try:
    from main_orchestraion import MainOrchestrator, DB_CONFIG
except ImportError:
    st.error("⚠️ Error: Could not find 'main_orchestraion.py'. Make sure you are running this from the 'llm_code' folder.")
    st.stop()

# --- 3. CACHING THE AGENT ---
# This ensures the heavy AI model loads only once, not on every message
@st.cache_resource
def load_agent():
    return MainOrchestrator()

# --- 4. SIDEBAR: DATABASE VIEWER ---
st.sidebar.title("🗄️ Database Viewer")
st.sidebar.caption("Live view of Docker SQL Data")

# Connection URL for Docker (Port 5433)
db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"

if st.sidebar.button("🔄 Refresh Table"):
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Fetch last 15 transactions
            query = "SELECT * FROM transactions ORDER BY date_and_time DESC LIMIT 15"
            df = pd.read_sql(query, conn)
            
        if not df.empty:
            st.sidebar.success("Connected!")
            st.sidebar.dataframe(df, use_container_width=True)
        else:
            st.sidebar.warning("Table found but it's empty.")
            
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed: {e}")
        st.sidebar.code(f"URL: {db_url}")

st.sidebar.markdown("---")
st.sidebar.info("**Tip:** Copy a 'Date' and 'Amount' from the table to test the agent!")

# --- 5. MAIN CHAT INTERFACE ---
st.title("🏦 RuPay Transaction Assistant")
st.markdown("Ask about **failed transactions** (SQL Tool) or **general rules** (RAG).")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load the Agent
with st.spinner("Initializing AI Agent..."):
    agent = load_agent()

# Display Previous Messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 6. USER INPUT HANDLING ---
if prompt := st.chat_input("Ex: Check failed withdrawal of 1500 rs..."):
    # Display User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Show a "Thinking..." spinner while the agent routes and queries
        with st.spinner("Processing..."):
            try:
                response = agent.chat(prompt, st.session_state.messages)
            except Exception as e:
                response = f"❌ **System Error:** {str(e)}"

        # Simulate typing effect
        message_placeholder.markdown(response)
        
    # Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": response})