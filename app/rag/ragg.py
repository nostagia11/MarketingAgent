import streamlit as st
import os
import dotenv
import uuid

from langchain_community.llms.ollama import Ollama

# check if it's linux so it works on Streamlit Cloud
if os.name == 'posix':
    __import__('pysqlite3')
    import sys

    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain.schema import HumanMessage, AIMessage

from app.rag.rag_methods import (
    load_doc_to_db,

    stream_llm_response,
    stream_llm_rag_response,
)



MODELS = [
    # "openai/o1-mini",
    "mistral:7b-instruct-q4_K_M"

]

st.set_page_config(
    page_title="RAG LLM app?",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Header ---
st.html("""<h2 style="text-align: center;">📚🔍 <i> Do your LLM even RAG bro? </i> 🤖💬</h2>""")

# --- Initial Setup ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]

# --- Side Bar LLM API Tokens ---
with st.sidebar:
    # --- Main Content ---

    st.divider()
    models = []
    for model in MODELS:
        if "mistral" in model:
            models.append(model)
    # elif "anthropic" in model and not missing_anthropic:
    #    models.append(model)

    st.selectbox(
        "🤖 Select a Model",
        options=models,
        key="model",
    )

    cols0 = st.columns(2)
    with cols0[0]:
        is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)
        st.toggle(
            "Use RAG",
            value=is_vector_db_loaded,
            key="use_rag",
            disabled=not is_vector_db_loaded,
        )

    with cols0[1]:
        st.button("Clear Chat", on_click=lambda: st.session_state.messages.clear(), type="primary")

    st.header("RAG Sources:")

    # File upload input for RAG with documents
    st.file_uploader(
        "📄 Upload a document",
        type=["pdf", "txt", "docx", "md"],
        accept_multiple_files=True,
        on_change=load_doc_to_db,
        key="rag_docs",
    )

    # URL input for RAG with websites


    with st.expander(f"📚 Documents in DB ({0 if not is_vector_db_loaded else len(st.session_state.rag_sources)})"):
        st.write([] if not is_vector_db_loaded else [source for source in st.session_state.rag_sources])

    # Main chat app
model_provider = st.session_state.model.split(":")[0]
if model_provider == "mistral":
    llm_stream = Ollama(

        model="mistral:7b-instruct-q4_K_M"
    )
# elif model_provider == "anthropic":

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        messages = [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
                    for m in st.session_state.messages]

        if not st.session_state.use_rag:
            st.write_stream(stream_llm_response(llm_stream, messages))
        else:
            st.write_stream(stream_llm_rag_response(llm_stream, messages))

with st.sidebar:
    st.divider()

    st.write(
        "📋[Medium Blog](https://medium.com/@enricdomingo/program-a-rag-llm-chat-app-with-langchain-streamlit-o1-gtp-4o-and-claude-3-5-529f0f164a5e)")
    st.write("📋[GitHub Repo](https://github.com/enricd/rag_llm_app)")
