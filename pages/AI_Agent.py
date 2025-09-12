from typing import Literal
from dataclasses import dataclass
import streamlit as st
import pandas as pd
from langchain.chains.conversation.base import ConversationChain
from langchain.memory import ConversationSummaryMemory
from langchain_community.llms.ollama import Ollama


# --- Sidebar or section navigation ---


# --- If user selects AI Assistant ---
# Input and button
#user_query = st.text_input("📝 Enter your question:")
#submit_button = st.button("Ask")

#if submit_button and user_query.strip():
# Simulated response (you can connect an AI backend here)
#   st.markdown("🧠 **Assistant Response:**")
#  st.success(f"You asked: _{user_query}_\n\nHere’s what I found... (AI logic goes here)")

#elif submit_button:
#   st.warning("❗ Please enter a question before submitting.")
@dataclass
class Message:
    """Class for keeping track of chat message."""
    origin: Literal["human", "ai"]
    message: str


def load_css():
    with open("static/style.css") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
        #define llm model
    if "conversation" not in st.session_state:
        llm = Ollama(model="mistral:7b-instruct-q4_K_M")

        st.session_state.conversation = ConversationChain(
            llm=llm,
            memory=ConversationSummaryMemory(llm=llm),

        )


initialize_session_state()

llm = Ollama(model="mistral:7b-instruct-q4_K_M")
conversation = ConversationChain(
    llm=llm,
    memory=ConversationSummaryMemory(llm=llm),
)


def on_click_callback():
    human_prompt = st.session_state.human_prompt
    llm_response = st.session_state.conversation.run(
        human_prompt,
    )
    #----------
    st.session_state.history.append(
        Message("human", human_prompt)
    )

    st.session_state.history.append(
        Message("AI", llm_response)
    )

    # ---------#


st.title(" AI Marketing Assistant")
chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")

with chat_placeholder:
    for chat in st.session_state.history:
        div = f"""
        <div class="chat-row 
        {'' if chat.origin == 'ai'  else 'row-reverse' }">
            <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat.origin == 'ai'
        else 'user_icon.png'}"
                 width=32 height=32>
                 <div class="chat-bubble
                 {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
                   &#8203;{chat.message}</div>
            """
        st.markdown(div, unsafe_allow_html=True)

with prompt_placeholder:
    st.markdown("chat")
    cols = st.columns((6, 1))
    cols[0].text_input(
        "Chat",
        #value="Ask Anything",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "submit",
        type="primary",
        on_click=on_click_callback,

    )
