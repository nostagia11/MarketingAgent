from langchain_community.llms.ollama import Ollama
from langchain.agents import initialize_agent, Tool, AgentType

from Db_query.posgresql_connector import run_sql_tool
from chartgeneration.chart_generation import PandasAITool
from chartgeneration.pandas_wrapper import create_pandas_tool


def get_tools():

 return [
        Tool(
            name="pandas_chart_generator",
            func=lambda prompt: "Dataset not loaded. Pandas tool must be created with a dataframe.",
            description="Use this tool to analyze the dataframe or generate charts from it.",
        ),

        Tool(
            name="sql_query_tool",
            description="Generate a correct SQL query from natural language and execute it on PostgreSQL.",
            func=run_sql_tool,
        )
    ]



