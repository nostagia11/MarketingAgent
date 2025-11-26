import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain_community.llms.ollama import Ollama
from langchain_core.tools import Tool

#from Db_query.posgresql_connector import run_sql_tool
from chartgeneration.chart_generation import PandasAITool
#from tools.pandasAI_tool import get_pandas_tool

"""pandas_tool = get_pandas_tool()
# Tools must be objects with .invoke(), not raw functions
tools_list = [run_sql_tool]
if pandas_tool:
    tools_list.append(pandas_tool)"""

"""llm = Ollama(model="qwen3:8b")
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
)"""
