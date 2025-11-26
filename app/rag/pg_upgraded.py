# Full integrated Streamlit RAG + Long-Term Memory (PostgreSQL + pgvector)
# This file merges your original RAG app with extracted-memory logic.
# Replace your current Streamlit app with this version and adjust import paths if needed.

import streamlit as st
import os
import uuid
import dotenv
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain_community.llms.ollama import Ollama
from langchain.schema import HumanMessage, AIMessage
from sentence_transformers import SentenceTransformer

# ---------------------- LONG-TERM MEMORY MODULES ------------------------
# These are embedded versions of the modules created in the canvas.
# You may move them into /app/rag/ later.

import psycopg2
from psycopg2.extras import RealDictCursor




# ============ CONFIG ============

DB_CONFIG = {
    "dbname": "marketing_agent",
    "user": "postgres",
    "password": "posgresql",
    "host": "localhost",
    "port": "5432"
}
# Embedding + LLM
#embedding_model = SentenceTransformer("all-MiniLM-L6-v2")




# ============ DATABASE FUNCTIONS ============

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

#DATABASE_URL = os.getenv("DATABASE_URL")  # MUST be set!

# ----- DB helpers -----
#def get_conn():
 #   if not DATABASE_URL:
  #      raise RuntimeError("DATABASE_URL env variable not set.")
   # return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    fact_text TEXT NOT NULL,
                    fact_type TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    embedding vector(384)
                );
                """
            )
    conn.close()

def insert_memory(user_id, fact_text, embedding, fact_type=None):
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO memories (user_id, fact_text, fact_type, embedding) VALUES (%s, %s, %s, %s)",
                (user_id, fact_text, fact_type, embedding),
            )
    conn.close()


def query_similar_memories(user_id, query_embedding, top_k=5):
    conn = get_conn()
    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT fact_text, fact_type, 1 - (embedding <#> %s) AS score FROM memories WHERE user_id = %s ORDER BY embedding <#> %s LIMIT %s",
                (query_embedding, user_id, query_embedding, top_k),
            )
            rows = cur.fetchall()
    conn.close()
    return rows

# ----- Memory extractor using LLM -----
from langchain.schema import HumanMessage
from app.rag.rag_methods import stream_llm_response, load_doc_to_db
from app.rag.Memory_methods import store_message, search_memory

EXTRACTION_INSTRUCTIONS = """
Extract ONLY long-term factual information from the user's message.
Return facts, one per line.
Tag each fact with: [JOB], [PROJECT], [BIO], [SKILL], etc.
If no facts exist, return an empty string.
"""


def extract_facts_from_message(llm, message):
    prompt = f"{EXTRACTION_INSTRUCTIONS}\n\nUser message:\n{message}\nFacts:"
    msgs = [HumanMessage(content=prompt)]
    result = ""
    for chunk in stream_llm_response(llm, msgs):
        result += chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
    return [f.strip() for f in result.splitlines() if f.strip()]

# ----- Fact embedding + storage -----
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def store_facts(user_id, facts):
    for fact in facts:
        fact_type = None
        text = fact
        if fact.startswith("[") and "]" in fact:
            idx = fact.index("]")
            fact_type = fact[1:idx]
            text = fact[idx+1:].strip()
        emb = embedding_model.encode(text).tolist()
        insert_memory(user_id, text, emb, fact_type)


def retrieve_relevant_facts(user_id, query, top_k=6):
    emb = embedding_model.encode(query).tolist()
    rows = query_similar_memories(user_id, emb, top_k=top_k)
    return [(r["fact_text"], r.get("fact_type"), float(r.get("score", 0))) for r in rows]

# Initialize DB
init_db()

# ---------------------- ORIGINAL APP ------------------------
MODELS = ["mistral:7b-instruct-q4_K_M"]

st.set_page_config(page_title="RAG LLM app?", page_icon="📚", layout="centered")
st.html("""<h2 style='text-align:center'>📚🔍 <i>Do your LLM even RAG bro?</i> 🤖💬</h2>""")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help you today?"},
    ]
if "conversation" not in st.session_state:
    llm_temp = Ollama(model="mistral:7b-instruct-q4_K_M")
    st.session_state.conversation = ConversationChain(llm=llm_temp, memory=ConversationSummaryMemory(llm=llm_temp))

# ---------------------- SIDEBAR ------------------------
with st.sidebar:
    models = [m for m in MODELS if "mistral" in m]
    st.selectbox("🤖 Select a Model", options=models, key="model")

    is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)

    cols = st.columns(2)
    with cols[0]:
        st.toggle("Use RAG", value=is_vector_db_loaded, key="use_rag", disabled=not is_vector_db_loaded)
    with cols[1]:
        st.button("Clear Chat", on_click=lambda: st.session_state.messages.clear())

    st.header("RAG Sources:")
    st.file_uploader("📄 Upload a document", type=["pdf", "txt", "docx", "md"], accept_multiple_files=True,
                     on_change=load_doc_to_db, key="rag_docs")

    with st.expander("Diagnostics"):
        st.write({"messages": len(st.session_state.messages)})

# ---------------------- MAIN CHAT ------------------------
model_provider = st.session_state.model.split(":")[0]
llm_stream = Ollama(model="mistral:7b-instruct-q4_K_M")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Your message"):

    # Append user msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    user_id = st.session_state.get("user_id", st.session_state.session_id)
    store_message(user_id, "user", prompt)

    # ---- Extract and Store Long-Term Facts ----
    extracted_facts = extract_facts_from_message(llm_stream, prompt)
    if extracted_facts:
        store_facts(user_id, extracted_facts)

    # ---- Retrieve relevant facts for this question ----
    relevant = retrieve_relevant_facts(user_id, prompt, top_k=6)
    facts_text = "\n".join([f"[{t}] {f}" if t else f for f, t, s in relevant])

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""

        # Memory injection
        if facts_text:
            enriched_prompt = f"""
            You are an AI assistant with long-term memory.

            Relevant user facts:
            {facts_text}

            User message: {prompt}
            Provide the best helpful response.
            """
        else:
            enriched_prompt = prompt

        for chunk in stream_llm_response(llm_stream, [HumanMessage(content=enriched_prompt)]):
            full += chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
            placeholder.markdown(full)

    # Save assistant response (after it's fully built)
    store_message(user_id, "assistant", full)
    st.session_state.messages.append({"role": "assistant", "content": full})
