import sys
import os
import tempfile
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Fix path to find database
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from db.database import init_db, get_all_bookings
from app.tools import create_booking_tool

load_dotenv()
init_db()

st.set_page_config(page_title="JetSet AeroBot", page_icon="✈️", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("✈️ JetSet Operations")
page = st.sidebar.radio("Go to:", ["Chat Assistant", "Admin Dashboard"])
st.sidebar.markdown("---")

# --- PAGE 1: CHAT ASSISTANT ---
if page == "Chat Assistant":
    st.title("✈️ AeroBot Assistant")

    # 1. AUTO-LOAD PDF
    pdf_name = "flight_policy.pdf"
    pdf_path_1 = os.path.join(project_root, pdf_name) 
    pdf_path_2 = os.path.join(current_dir, pdf_name)

    final_path = None
    if os.path.exists(pdf_path_1): final_path = pdf_path_1
    elif os.path.exists(pdf_path_2): final_path = pdf_path_2

    if "vectorstore" not in st.session_state:
        if final_path:
            with st.spinner("🧠 Waking up Brain..."):
                try:
                    loader = PyPDFLoader(final_path)
                    docs = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    splits = text_splitter.split_documents(docs)
                    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                    st.session_state.vectorstore = FAISS.from_documents(splits, embeddings)
                except Exception as e:
                    st.error(f"❌ Brain Error: {e}")

    # 2. STATUS INDICATOR
    if st.session_state.get("vectorstore"):
        st.sidebar.success("🟢 Brain: ONLINE")
    else:
        st.sidebar.error("🔴 Brain: OFFLINE")

    # 3. SETUP AI
    grok_api_key = os.getenv("GROQ_API_KEY")
    if not grok_api_key:
        st.error("Missing GROQ_API_KEY in .env")
        st.stop()

    llm = ChatOpenAI(
        api_key=grok_api_key,
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    if "agent_memory" not in st.session_state:
        st.session_state.agent_memory = MemorySaver()

    tools = [create_booking_tool]
    agent_executor = create_react_agent(llm, tools, checkpointer=st.session_state.agent_memory)

    # 4. CHAT UI
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("How can I help you?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Force-Feed Context
        context_text = ""
        if st.session_state.get("vectorstore"):
            retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 2})
            relevant_docs = retriever.invoke(prompt)
            context_text = "\n\n".join([d.page_content for d in relevant_docs])
        
        augmented_prompt = f"""
        You are a helpful assistant for JetSet Aviation.
        POLICY INFO: {context_text}
        USER QUESTION: {prompt}
        INSTRUCTIONS: Use POLICY INFO to answer. If booking, use 'create_booking_tool'.
        """

        with st.chat_message("assistant"):
            with st.expander("👀 See Internal Thinking"):
                st.write(f"**Retrieved Context:** {context_text[:300]}...")
            with st.spinner("Thinking..."):
                try:
                    config = {"configurable": {"thread_id": "1"}}
                    response = agent_executor.invoke({"messages": [("user", augmented_prompt)]}, config)
                    ai_message = response["messages"][-1].content
                    st.write(ai_message)
                    st.session_state.messages.append({"role": "assistant", "content": ai_message})
                except Exception as e:
                    st.error(f"Error: {e}")

# --- PAGE 2: ADMIN DASHBOARD (DATABASE VIEW) ---
elif page == "Admin Dashboard":
    st.title("📋 Admin Database View")
    st.write("Live data from `aviation.db`")
    
    # Password Protection
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":
        # Fetch Data
        data = get_all_bookings()
        
        if data:
            # Convert to pretty DataFrame
            df = pd.DataFrame(data, columns=["ID", "Name", "Email", "Service", "Date", "Time"])
            st.dataframe(df, use_container_width=True)
            
            st.success(f"Total Bookings: {len(data)}")
        else:
            st.info("No bookings found in database yet.")
            
    elif password:
        st.error("Incorrect Password")