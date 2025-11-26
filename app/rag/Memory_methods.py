import streamlit as st
import psycopg2
import ollama
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import datetime

# ============ CONFIG ============

DB_CONFIG = {
    "dbname": "marketing_agent",
    "user": "postgres",
    "password": "posgresql",
    "host": "localhost",
    "port": "5432"
}
# Embedding + LLM
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
#client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))  # or set via env



# ============ DATABASE FUNCTIONS ============

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def store_message(user_id, role, content):
    """Embed and store the chat message."""
    embedding = embedding_model.encode(content).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO chat_memory (user_id, role, content, embedding)
        VALUES (%s, %s, %s, %s)
    """, (user_id, role, content, embedding))
    conn.commit()
    cur.close()
    conn.close()


def search_memory(user_id, query, top_k=5):
    """Retrieve most similar messages for context."""
    query_embedding = embedding_model.encode(query).tolist()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM chat_memory
        WHERE user_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """, (query_embedding, user_id, query_embedding, top_k))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


