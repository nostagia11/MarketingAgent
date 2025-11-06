"""import uuid

import streamlit as st
from langchain_community.llms.ollama import Ollama
from data import load_data
import os
import pandas as pd


#from pandasai.callbacks import BaseCallback
from pandasai.responses.response_parser import ResponseParser
import streamlit as st
import pandas as pd
from langchain_community.llms.ollama import Ollama
from langchain.agents import initialize_agent, Tool, AgentType
from pandasai import SmartDataframe


class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
      st.dataframe(result["value"])
      return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return
class PandasAITool:
    def __init__(self, df, llm):
        self.df = df
        self.smart_df = SmartDataframe(df, config = {
        "llm": llm,
        "response_parser": StreamlitResponse,
        "verbose": True,  # prints code + steps
        "save_logs": True,

    }, )

    def run(self, query: str):
        Runs query through SmartDataframe (chart or analysis).
        result = self.smart_df.chat(query)
        return str(result)


# ---------- SESSION STATE ----------
if "dashboard_charts" not in st.session_state:
    st.session_state["dashboard_charts"] = []
st.title("chart generation")

uploaded_file = st.file_uploader("Upload your file", type=["csv","xls"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander("Dataframe preview"):
        st.write(df.tail(10))

else:
    st.warning("Please upload a CSV file.")






query = st.text_area("chat with dataframe")
#st.text_input("💬 Ask something (e.g., 'Plot sales vs month'):")
container = st.container()

# Load your dataset
#df = pd.read_csv("your_dataset.csv")


if query:
    llm = Ollama(model="qwen3:8b")

    # Define PandasAI Tool
    pandas_tool = PandasAITool(df, llm)
    tools = [
        Tool(
            name="pandas_chart_generator",
            func=pandas_tool.run,
            description="Use this tool to analyze the dataframe or generate charts from it.",
        )
    ]

    # Initialize Agent
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )



#-------------


if st.button("Submit"):
    if agent is not None and query:
        with st.spinner("Agent thinking..."):
            try:
                response = agent.run(query)
                chart = pandas_tool.run(query)
                st.session_state["last_chart"] = chart
                st.pyplot(chart)
                # use .run() not .query()
                st.markdown("### 🤖 Agent Response")
                # st.write(response)
                st.write(response)
            except Exception as e:
                st.error(f"Error generating chart: {e}")

    elif agent is None:
        st.warning("⚠️ Please upload a CSV file first.")
    elif not query:
        st.warning("⚠️ Please enter a query before submitting.")

# ---------- ADD TO DASHBOARD ----------
if "last_chart" in st.session_state:
    if st.button("➕ Add to Dashboard"):
        chart_id = str(uuid.uuid4())
        st.session_state["dashboard_charts"].append({
            "id": chart_id,
            "title": query,
            "figure": st.session_state["last_chart"]
        })
        st.success("✅ Chart added to dashboard!")

st.page_link("chartgeneration/dashboard_builder.py", label="➡️ Go to Dashboard", icon="📊")"""
import uuid
import streamlit as st
from langchain_community.llms.ollama import Ollama
from langchain.agents import initialize_agent, Tool, AgentType
from pandasai import SmartDataframe
from pandasai.responses.response_parser import ResponseParser
import pandas as pd


# ---------- RESPONSE PARSER ----------
class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return


# ---------- PANDASAI TOOL ----------
class PandasAITool:
    def __init__(self, df, llm):
        self.df = df
        self.smart_df = SmartDataframe(
            df,
            config={
                "llm": llm,
                "response_parser": StreamlitResponse,
                "verbose": False,
                "save_logs": True,
                "enable_cache": True,
                "use_error_correction_framework": False,
                "save_charts": False,  # prevent PandasAI from saving charts to disk
                "custom_plotting": True,
            },
        )

    def run(self, query: str):
        """Runs query through SmartDataframe (chart or analysis)."""
        result = self.smart_df.chat(query)
        return str(result)


# ---------- SESSION STATE INITIALIZATION ----------
if "dashboard_charts" not in st.session_state:
    st.session_state["dashboard_charts"] = []

if "messages" not in st.session_state:
    st.session_state["messages"] = []  # store full chat history

st.title("📊 AI Chart Generation Assistant")


# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("📂 Upload your dataset", type=["csv", "xls", "xlsx"])
df = None

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    with st.expander("📘 Dataframe Preview"):
        st.write(df.tail(10))
else:
    st.warning("Please upload a CSV or Excel file.")


# ---------- CHAT INTERFACE ----------
st.subheader("💬 Chat with your data")

# Display previous conversation
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box for user query
if prompt := st.chat_input("Ask something (e.g., 'Plot sales vs month')"):
    st.session_state["messages"].append({"role": "user", "content": prompt})

    if df is not None:
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
                        st.write(result)

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
        st.warning("⚠️ Please upload a dataset first.")
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
