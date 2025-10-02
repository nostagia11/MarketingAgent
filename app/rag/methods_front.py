import streamlit as st
from langchain_community.llms.ollama import Ollama

from app.rag.rag_methods import load_doc_to_db, stream_llm_rag_response

st.set_page_config(page_title="RAG Assistant", layout="wide")

# --- Initialize session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_docs" not in st.session_state:
    st.session_state.rag_docs = []

if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []

if "session_id" not in st.session_state:
    st.session_state.session_id = "rag_session"

# --- Sidebar: Document Loader ---
st.sidebar.header("📄 Document Loader")
uploaded_files = st.sidebar.file_uploader(
    "Upload documents (PDF, DOCX, TXT, MD)",
    type=["pdf", "docx", "txt", "md"],
    accept_multiple_files=True
)

if uploaded_files:
    st.session_state.rag_docs = uploaded_files
    if st.sidebar.button("Load to Vector DB"):
        load_doc_to_db()

# --- Chat Interface ---
st.title("💬 RAG Assistant with Ollama")

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if user_query := st.chat_input("Ask me something..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Assistant streaming response
    with st.chat_message("assistant"):
        llm = Ollama(model="mistral:7b-instruct-q4_K_M")  # Example model, replace with yours
        response_stream = stream_llm_rag_response(llm, st.session_state.messages)
        response_box = st.empty()
        full_response = ""

        for chunk in response_stream:
            full_response += str(chunk)
            response_box.markdown(full_response)
