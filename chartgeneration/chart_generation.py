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
        """Runs query through SmartDataframe (chart or analysis)."""
        result = self.smart_df.chat(query)
        return str(result)

st.title("chart generation")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander("Dataframe preview"):
        st.write(df.tail(10))

else:
    st.warning("Please upload a CSV file.")






query = st.text_area("chat with dataframe")
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
            response = agent.run(query)  # use .run() not .query()
            st.markdown("### 🤖 Agent Response")
            st.write(response)
    elif agent is None:
        st.warning("⚠️ Please upload a CSV file first.")
    elif not query:
        st.warning("⚠️ Please enter a query before submitting.")
