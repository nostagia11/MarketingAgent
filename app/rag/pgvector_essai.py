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


# ============ STREAMLIT UI ============

st.title("🧠 LLM Chat with Long-Term Memory (PostgreSQL + pgvector)")

#user_id = st.text_input("Enter your user ID:", "user_1")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.chat_input("Say something...")

if user_input:
    # Store user message
    store_message(st.session_state.user_id, "user", user_input)

    # Retrieve relevant past context
    context_results = search_memory(st.session_state.user_id, user_input)
    context_text = "\n".join([r[0] for r in context_results])

    # Combine memory context with user input
    prompt = f"""
    You are a helpful AI assistant with memory.
    Here are relevant past memories from the user's chat history:
    {context_text}

    Current message: {user_input}
    Provide a natural, helpful response that uses the context when relevant.
    """

    # Query the LLM (OpenAI example)
   # response = client.chat.completions.create(
   #     model="gpt-3.5-turbo",
    #    messages=[{"role": "user", "content": prompt}],
    #    max_tokens=300
    #)

    # Query the local Mistral model through Ollama
    response = ollama.chat(
        model="mistral:7b-instruct-q4_K_M",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response["message"]["content"]
    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("assistant", answer))

    # Store assistant reply
    store_message(st.session_state.user_id, "assistant", answer)

# Display conversation
for role, text in st.session_state.history:
    if role == "user":
        st.chat_message("user").write(text)
    else:
        st.chat_message("assistant").write(text)
