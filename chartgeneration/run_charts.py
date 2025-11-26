import uuid

import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms.ollama import Ollama
from langchain_core.tools import Tool

from Db_query.connector import pg_connection_widget
from Db_query.posgresql_connector import init_sql_chain
from chartgeneration.chart_generation import PandasAITool
from chartgeneration.connect_to_db import connect_to_db
#from langchain.agents import initialize_agent, Tool, AgentType

#from chartgeneration.pandas_wrapper import create_pandas_tool
#from pandasai import SmartDataframe
#from pandasai.responses.response_parser import ResponseParser
import pandas as pd

#from tools.agent_langchain import agent

# ---------- SESSION STATE INITIALIZATION ----------
if "dashboard_charts" not in st.session_state:
    st.session_state["dashboard_charts"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = []  # store full chat history

st.title("📊 AI Chart Generation Assistant")

# ---------- DB CONN ----------
st.session_state.engine = None
if "df" not in st.session_state:
    st.session_state["df"] = None
connect_to_db()  # this should set st.session_state.engine
df = None

# ---------- TRY TO LOAD DF FROM DATABASE ----------
if st.session_state.engine is not None:
    try:
        st.info("Loading data from database...")
        query = "SELECT * FROM marketing_campaign LIMIT 100"

        st.write("Running Query:", query)
        st.write("Engine:", st.session_state.engine)

        df = pd.read_sql(query, st.session_state.engine)
        st.session_state.df = df
        st.success("Data loaded from database!")
    except Exception as e:
        st.warning(f"Could not load from DB: {e}")
        df = None

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("📂 Upload your dataset", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    # File upload OVERRIDES the DB data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.session_state.df = df
    st.success("Data loaded from uploaded file!")

# ---------- PREVIEW ----------
if df is not None:
    with st.expander("📘 Dataframe Preview"):
        st.write(df.tail(10))
else:
    st.warning("Please upload a CSV/Excel file or connect to the database.")

# ---------- CHAT INTERFACE ----------
st.subheader("💬 Chat with your data")

# Display previous conversation
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box for user query
if prompt := st.chat_input("Ask something (e.g., 'Plot sales vs month')"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    #-------------------
    llm = Ollama(model="qwen3:8b")
    pandas_tool = PandasAITool(df, llm)
    tools = [
        Tool(
            name="pandas_chart_generator",
            func=pandas_tool.run,
            description="Use this tool to analyze the dataframe or generate charts from it.",
        )
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    if df is not None:
        llm = Ollama(model="qwen3:8b")

        pandas_tool = PandasAITool(df=df, llm=llm)

        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Run both the agent and PandasAI
                    response = agent.run(prompt)
                    result = pandas_tool.run(prompt)

                    # Try to detect chart or text result
                    if hasattr(result, "savefig"):  # Matplotlib figure
                        st.pyplot(result)
                        st.session_state["last_chart"] = result
                    elif isinstance(result, pd.DataFrame):
                        st.dataframe(result)
                    else:
                        st.write(response)

                    # Display the text response from the agent
                    st.markdown("### 🤖 Agent Response")
                    st.write(response)

                    # Store assistant reply in chat history
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": str(response)}
                    )

                except Exception as e:
                    st.error(f"Error generating chart: {e}")
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": f"⚠️ Error: {e}"}
                    )



    else:
        st.warning("⚠️ Please upload a dataset first or connect to DB")
        st.session_state["messages"].append(
            {"role": "assistant", "content": "⚠️ Please upload a dataset first."}
        )

# ---------- ADD TO DASHBOARD ----------
if "last_chart" in st.session_state:
    if st.button("➕ Add to Dashboard"):
        chart_id = str(uuid.uuid4())
        st.session_state["dashboard_charts"].append(
            {"id": chart_id, "title": prompt, "figure": st.session_state["last_chart"]}
        )
        st.success("✅ Chart added to dashboard!")

st.page_link("chartgeneration/dashboard_builder.py", label="➡️ Go to Dashboard", icon="📊")
