import streamlit as st
import os
import uuid
import psycopg2
import ollama
from sentence_transformers import SentenceTransformer

from langchain.schema import HumanMessage, AIMessage
from langchain_community.llms.ollama import Ollama

# -----------------------------
# IMPORT EXISTING RAG FUNCTIONS
# -----------------------------
from app.rag.rag_methods import (
    load_doc_to_db,
    stream_llm_response,
    stream_llm_rag_response,
)

# -----------------------------
# PGVECTOR MEMORY CONFIG
# -----------------------------
DB_CONFIG = {
    "dbname": "marketing_agent",
    "user": "postgres",
    "password": "posgresql",
    "host": "localhost",
    "port": "5432"
}

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def pg_store_message(user_id, role, content):
    """Store message in pgvector DB."""
    emb = embedding_model.encode(content).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_memory (user_id, role, content, embedding)
        VALUES (%s, %s, %s, %s)
    """, (user_id, role, content, emb))
    conn.commit()
    cur.close()
    conn.close()

def pg_search_memory(user_id, query, top_k=5):
    """Retrieve similar memories from pgvector."""
    emb = embedding_model.encode(query).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT content
        FROM chat_memory
        WHERE user_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (user_id, emb, top_k))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in results]

# -----------------------------
# STREAMLIT + SESSION STATE
# -----------------------------
st.set_page_config(page_title="RAG + Memory Chatbot", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "short_memory_window" not in st.session_state:
    st.session_state.short_memory_window = 6   # last N messages

if "use_longterm_memory" not in st.session_state:
    st.session_state.use_longterm_memory = True


# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.header("Settings")

    st.toggle("Use RAG", key="use_rag")
    st.toggle("Use long-term memory (pgvector)", key="use_longterm_memory")

    st.number_input("Short-term memory window:", 2, 20,
                    key="short_memory_window")

    st.button("Clear Chat", on_click=lambda: st.session_state.messages.clear())

    st.subheader("Upload RAG documents")
    st.file_uploader("Docs:", type=["pdf", "txt", "md", "docx"],
                     accept_multiple_files=True,
                     on_change=load_doc_to_db,
                     key="rag_docs")


# -----------------------------
# DISPLAY CHAT MESSAGES
# -----------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])


# -----------------------------
# USER INPUT
# -----------------------------
prompt = st.chat_input("Your message")

if prompt:

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # -------- SHORT-TERM MEMORY ----------
    short_memory = st.session_state.messages[-st.session_state.short_memory_window:]

    short_memory_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in short_memory
    )

    # -------- LONG-TERM MEMORY (PGVECTOR) ----------
    if st.session_state.use_longterm_memory:
        long_memory_hits = pg_search_memory(st.session_state.session_id, prompt, top_k=5)
        long_memory_text = "\n".join(long_memory_hits)
    else:
        long_memory_text = ""

    # -------- BUILD FINAL CONTEXT FOR LLM ----------
    system_context = f"""
You are an AI assistant.

SHORT-TERM MEMORY:
{short_memory_text}

LONG-TERM MEMORY:
{long_memory_text}

Respond naturally. Use memories ONLY if relevant.
"""

    messages = [
        AIMessage(content=system_context),
        HumanMessage(content=prompt)
    ]

    # -------- STREAM RESPONSE ----------
    with st.chat_message("assistant"):
        if not st.session_state.use_rag:
            response_stream = stream_llm_response(Ollama(model="mistral:7b-instruct-q4_K_M"), messages)
        else:
            response_stream = stream_llm_rag_response(Ollama(model="mistral:7b-instruct-q4_K_M"), messages)

        full_answer = st.write_stream(response_stream)

    # Add assistant response to UI memory
    st.session_state.messages.append({"role": "assistant", "content": full_answer})

    # Store to long-term memory DB
    if st.session_state.use_longterm_memory:
        pg_store_message(st.session_state.session_id, "user", prompt)
        pg_store_message(st.session_state.session_id, "assistant", full_answer)
