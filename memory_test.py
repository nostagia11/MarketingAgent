import streamlit as st
import os
import dotenv
import uuid
import asyncio

from langchain_community.llms.ollama import Ollama
from langchain.schema import HumanMessage, AIMessage

# Import your RAG helper methods
from app.rag.rag_methods import (
    load_doc_to_db,
    stream_llm_response,
    stream_llm_rag_response,
)

# Agno imports for memory
from agno.agent import Agent


dotenv.load_dotenv()

MODELS = [
    "mistral:7b-instruct-q4_K_M",
]

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="🧠 RAG + Persistent Memory Chatbot",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.html("""<h2 style="text-align: center;">📚🔍 <i>RAG + Memory Chatbot</i> 🤖💬</h2>""")

# --- Session Setup ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]

if "user_id" not in st.session_state:
    st.session_state.user_id = "demo_user"

# --- Sidebar ---
with st.sidebar:
    st.text_input("🧑 User ID", key="user_id", value=st.session_state.user_id)

    st.divider()

    models = [m for m in MODELS if "mistral" in m]
    st.selectbox("🤖 Select a Model", options=models, key="model")

    cols = st.columns(2)
    with cols[0]:
        is_vector_db_loaded = ("vector_db" in st.session_state and st.session_state.vector_db is not None)
        st.toggle("Use RAG", value=is_vector_db_loaded, key="use_rag", disabled=not is_vector_db_loaded)
    with cols[1]:
        st.button("Clear Chat", on_click=lambda: st.session_state.messages.clear(), type="primary")

    st.header("RAG Sources:")
    st.file_uploader(
        "📄 Upload a document",
        type=["pdf", "txt", "docx", "md"],
        accept_multiple_files=True,
        on_change=load_doc_to_db,
        key="rag_docs",
    )
    with st.expander(f"📚 Documents in DB ({0 if not is_vector_db_loaded else len(st.session_state.rag_sources)})"):
        st.write([] if not is_vector_db_loaded else [source for source in st.session_state.rag_sources])

# --- LLM Initialization ---
model_provider = st.session_state.model.split(":")[0]
if model_provider == "mistral":
    llm_stream = Ollama(model=st.session_state.model)

# --- Agno Persistent Memory Integration ---
# --- Agno Persistent Memory Integration (PostgreSQL Version) ---
from agno.agent import Agent
from agno.db.postgres import PostgresDb

class ProductionMemoryAgent:
    def __init__(self, user_id: str):
        self.user_id = user_id

        # ✅ Step 1: Setup PostgreSQL memory database
        self.db = PostgresDb(
            db_url=os.getenv("POSTGRES_URL", "postgresql://posgres:posgresql@localhost:5432/marketing_agent"),
            memory_table="user_memory",  # Table where memories are stored
        )

        # ✅ Step 2: Create the agent with PostgreSQL-backed memory
        self.agent = Agent(
            db=self.db,
            model="mistral:7b-instruct-q4_K_M",  # Local Ollama model
            instructions="""
            You are a helpful AI assistant that remembers all prior user conversations.
            Use the PostgreSQL memory to recall previous messages by this user and answer coherently.
            """
        )

    async def chat(self, message: str) -> str:
        # ✅ Store and generate a contextual response
        response = await asyncio.to_thread(self.agent.run, message, user_id=self.user_id)
        return response

    async def get_memory_summary(self) -> int:
        # ✅ Retrieve all memories for the current user
        memories = await asyncio.to_thread(self.agent.get_user_memories, self.user_id)
        return len(memories)


# Create or reuse memory agent for this session
if "memory_agent" not in st.session_state or st.session_state.memory_agent.user_id != st.session_state.user_id:
    st.session_state.memory_agent = ProductionMemoryAgent(st.session_state.user_id)

memory_agent = st.session_state.memory_agent

# --- Display Chat Messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input + Response ---
if prompt := st.chat_input("Your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Convert messages to LangChain format
        messages = [
            HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"])
            for m in st.session_state.messages
        ]

        # Case 1: If RAG is used, combine with retrieval-augmented response
        if st.session_state.use_rag:
            response_stream = stream_llm_rag_response(llm_stream, messages)
            st.write_stream(response_stream)
        else:
            # Case 2: Otherwise, use persistent memory agent
            async def get_response():
                return await memory_agent.chat(prompt)

            response = asyncio.run(get_response())
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- Memory Summary Button ---
if st.button("📊 Show Memory Summary"):
    total_memories = asyncio.run(memory_agent.get_memory_summary())
    st.info(f"🧠 Total Memories Stored for {st.session_state.user_id}: {total_memories}")


    st.write("📋[Medium Blog](https://medium.com/@enricdomingo/program-a-rag-llm-chat-app-with-langchain-streamlit-o1-gtp-4o-and-claude-3-5-529f0f164a5e)")
    st.write("📋[GitHub Repo](https://github.com/enricd/rag_llm_app)")
