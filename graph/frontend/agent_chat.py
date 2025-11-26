import streamlit as st
from graph.build_graph import build_graph


graph_agent = build_graph()

def agent_chat():
    st.title("🧠 Router Agent (SQL + Charts + Chat)")

    # ---- SHOW DATAFRAME BEFORE CHAT INPUT ----
    if st.session_state.get("db_connected") and "df" in st.session_state:
        st.subheader("📊 Loaded Database Table")
        st.dataframe(st.session_state.df)

    st.write("---")  # divider before chat

    # ---- Conversation history ----
    if "history" not in st.session_state:
        st.session_state.history = []

    for role, msg in st.session_state.history:
        with st.chat_message(role):
            st.write(msg)

    # ---- Chat Input ----
    prompt = st.chat_input("Ask something...")

    if prompt:
        st.session_state.history.append(("user", prompt))

        # Run graph
        result = graph_agent.invoke({"input": prompt})
        from tools.utils import strip_think

        answer = strip_think(result["output"])

        st.session_state.history.append(("assistant", answer))

        with st.chat_message("assistant"):
            st.write(answer)