"""
Merged Streamlit RAG app with long-term vector memory (embedding stored in PostgreSQL)
Now includes short-term conversational memory using LangChain ConversationSummaryMemory.
"""

import os
import time
import uuid
from datetime import datetime
import json
import math

import streamlit as st
from sqlalchemy import create_engine, text
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer

# LangChain / RAG imports
from langchain_community.llms.ollama import Ollama
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain.schema import HumanMessage, AIMessage
from app.rag.rag_methods import (
    load_doc_to_db,
    stream_llm_response,
    stream_llm_rag_response,
)

# --- Configuration / Init ---
st.set_page_config(page_title="Merged RAG + Memory App", layout="centered")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # small & effective
_embedding_model = None
DB_TABLE = "memories"

# --- Short-term memory initialization ---
def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversation" not in st.session_state:
        llm = Ollama(model="mistral:7b-instruct-q4_K_M")
        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),
        )

initialize_session_state()

# --- Helpers: Embeddings ---
@st.cache_resource
def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model

def embed_text(text: str):
    model = get_embedding_model()
    vec = model.encode(text)
    return vec.tolist()

# --- Helpers: simple cosine similarity ---
def cosine_similarity(a, b):
    if a is None or b is None:
        return -1
    dot = sum(x*y for x,y in zip(a,b))
    norma = math.sqrt(sum(x*x for x in a))
    normb = math.sqrt(sum(x*x for x in b))
    if norma == 0 or normb == 0:
        return -1
    return dot / (norma * normb)

# --- Database (Postgres) memory table management ---
@st.cache_resource
def get_sqlalchemy_engine():
    if "engine" in st.session_state and st.session_state.engine is not None:
        return st.session_state.engine
    if "postgres" in st.secrets:
        p = st.secrets["postgres"]
        uri = (
            f"postgresql+psycopg2://{p['user']}:{p['password']}@{p['host']}:{p['port']}/{p['dbname']}"
        )
        engine = create_engine(uri)
        return engine
    else:
        return None


def init_memory_table():
    engine = get_sqlalchemy_engine()
    if engine is None:
        return False
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {DB_TABLE} (
        id SERIAL PRIMARY KEY,
        user_id TEXT,
        role TEXT,
        content TEXT,
        embedding JSONB,
        created_at TIMESTAMP
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_sql))
    return True


def store_message(user_id: str, role: str, content: str):
    engine = get_sqlalchemy_engine()
    if engine is None:
        st.warning("No DB engine available to store memory.")
        return
    emb = embed_text(content)
    now = datetime.utcnow()
    insert_sql = f"INSERT INTO {DB_TABLE} (user_id, role, content, embedding, created_at) VALUES (:user_id, :role, :content, :embedding::jsonb, :created_at)"
    params = {
        "user_id": user_id,
        "role": role,
        "content": content,
        "embedding": json.dumps(emb),
        "created_at": now,
    }
    with engine.connect() as conn:
        conn.execute(text(insert_sql), params)


def search_memory(user_id: str, query: str, top_k: int = 5):
    engine = get_sqlalchemy_engine()
    if engine is None:
        return []
    q_emb = embed_text(query)
    select_sql = f"SELECT id, role, content, embedding, created_at FROM {DB_TABLE} WHERE user_id = :user_id"
    rows = []
    with engine.connect() as conn:
        res = conn.execute(text(select_sql), {"user_id": user_id})
        for r in res:
            emb = r[3]
            if isinstance(emb, str):
                try:
                    emb_list = json.loads(emb)
                except Exception:
                    emb_list = None
            else:
                emb_list = emb
            rows.append((r[0], r[1], r[2], emb_list, r[4]))

    scored = []
    for (id_, role, content, emb, created_at) in rows:
        score = cosine_similarity(q_emb, emb) if emb else -1
        scored.append((score, role, content, created_at))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(role, content, score, created_at) for (score, role, content, created_at) in scored[:top_k]]

# --- App session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]

# --- Sidebar ---
MODELS = ["mistral:7b-instruct-q4_K_M"]

with st.sidebar:
    st.header("Settings")
    st.selectbox("Select a Model", options=MODELS, key="model")
    is_vector_db_loaded = st.session_state.vector_db is not None
    use_rag = st.checkbox("Use RAG (documents)", value=is_vector_db_loaded)
    st.file_uploader("Upload doc(s)", type=["pdf", "txt", "docx", "md"], accept_multiple_files=True, on_change=load_doc_to_db, key="rag_docs")

# Initialize memory DB
init_memory_table()

# --- LLM setup ---
llm_stream = Ollama(model=st.session_state.model)

# --- Chat UI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


    user_input = st.chat_input("Your message")
    submitted = st.form_submit_button("Submit")

if submitted and user_input:
    user_id = st.session_state.get("user_id", st.session_state.session_id)
    store_message(user_id, "user", user_input)
    memory_ctx = search_memory(user_id, user_input, top_k=5)
    memory_text = "\n".join([f"[{r[2]}]" for r in memory_ctx]) if memory_ctx else ""

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Short-term memory usage
        conversation = st.session_state.conversation
        conversation.memory.save_context({"input": user_input}, {"output": full_response})

        messages = [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m in st.session_state.messages]

        try:
            if use_rag and st.session_state.vector_db is not None:
                if memory_text:
                    messages.insert(0, HumanMessage(content=f"Relevant memory context:\n{memory_text}"))
                for chunk in stream_llm_rag_response(llm_stream, messages):
                    full_response += chunk
                    message_placeholder.markdown(full_response)
            else:
                if memory_text:
                    messages.insert(0, HumanMessage(content=f"Relevant memory context:\n{memory_text}"))
                for chunk in stream_llm_response(llm_stream, messages):
                    full_response += chunk.content if hasattr(chunk, 'content') else str(chunk)
                    message_placeholder.markdown(full_response)

            store_message(user_id, "assistant", full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Error generating response: {e}")

with st.expander("Diagnostics / Debug"):
    st.write({
        "session_id": st.session_state.session_id,
        "vector_db_loaded": st.session_state.vector_db is not None,
        "messages_len": len(st.session_state.messages),
    })
