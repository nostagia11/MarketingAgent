import streamlit as st
import os
import dotenv
import uuid

from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain_community.llms.ollama import Ollama

# check if it's linux so it works on Streamlit Cloud
#if os.name == 'posix':
#    __import__('pysqlite3')
#   import sys

#   sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from langchain.schema import HumanMessage, AIMessage
from sentence_transformers import SentenceTransformer

from app.rag.Memory_methods import store_message, search_memory
from app.rag.rag_methods import (
    load_doc_to_db,

    stream_llm_response,
    stream_llm_rag_response,
)

MODELS = [

    "mistral:7b-instruct-q4_K_M",

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
#if "vector_db" not in st.session_state:
 #   st.session_state.vector_db = None

if "rag_sources" not in st.session_state:
    st.session_state.rag_sources = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
    ]
if "conversation" not in st.session_state:
    llm_temp = Ollama(model="mistral:7b-instruct-q4_K_M")
    st.session_state.conversation = ConversationChain(
        llm=llm_temp,
        memory=ConversationSummaryMemory(llm=llm_temp),
    )
if "history" not in st.session_state:
    st.session_state.history = []
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Side Bar LLM API Tokens ---
with st.sidebar:
    # --- Main Content ---

    # Sidebar

    st.divider()
    models = []
    for model in MODELS:
        if "mistral" in model:
            models.append(model)

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

    with st.expander(f"📚 Documents in DB ({0 if not is_vector_db_loaded else len(st.session_state.rag_sources)})"):
        st.write([] if not is_vector_db_loaded else [source for source in st.session_state.rag_sources])

    # Main chat app
model_provider = st.session_state.model.split(":")[0]
if model_provider == "mistral":
    llm_stream = Ollama(
        model="mistral:7b-instruct-q4_K_M"
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    user_id = st.session_state.get("user_id", st.session_state.session_id)
    store_message(user_id, "user", prompt)
    memory_ctx = search_memory(user_id, prompt)
    context_text = "\n".join([r[0] for r in memory_ctx])
    st.markdown(context_text)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        # Short-term memory usage
        conversation = st.session_state.conversation
        conversation.memory.save_context({"input": prompt}, {"output": full_response})

        messages = [HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m
                    in st.session_state.messages]
        st.session_state.history.append(("user", prompt))

        try:

                # Combine long-term memory context with user prompt
                if context_text:
                    prompt_with_memory = f"""
                    You are a helpful AI assistant with memory.
                    Here are relevant past memories from the user's chat history:
                    {context_text}

                    Current message: {prompt}
                    Provide a natural, helpful response that uses the context when relevant.
                    """
                else:
                    prompt_with_memory = prompt

                # Run the model using the enriched prompt
                #for chunk in stream_llm_response(llm_stream, [HumanMessage(content=prompt_with_memory)]):
                #    full_response += chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
                 #   message_placeholder.markdown(full_response)
                messages_to_model = [
                    HumanMessage(content=prompt_with_memory)
                ]
                for chunk in stream_llm_response(llm_stream, messages_to_model):
                    full_response += chunk if isinstance(chunk, str) else getattr(chunk, "content", "")
                    message_placeholder.markdown(full_response)


        except Exception as e:
            st.error(f"Error generating response: {e}")

        store_message(user_id, "assistant", full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.history.append(("assistant", full_response))





with st.sidebar:

    with st.expander("Diagnostics / Debug"):
        st.write({
            "session_id": st.session_state.session_id,

            "messages_len": len(st.session_state.messages),
            "history": st.session_state.history,
        })
