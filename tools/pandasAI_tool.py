"""import streamlit as st
from langchain_community.llms.ollama import Ollama

from chartgeneration.pandas_wrapper import create_pandas_tool

if "df_db" not in st.session_state:
    st.session_state.df_db = None

llm = Ollama(model="mistral:7b-instruct-q4_K_M")
pandas_tool = create_pandas_tool(st.session_state.df_db, llm)"""
import streamlit as st
from chartgeneration.pandas_wrapper import create_pandas_tool
from langchain_community.llms.ollama import Ollama


def get_pandas_tool():
    """Create pandasAI tool ONLY when needed."""
    if "df_db" not in st.session_state or st.session_state.df_db is None:
        return None  # No dataframe available

    if "llm" not in st.session_state:
        st.session_state.llm = Ollama(model="mistral:7b-instruct-q4_K_M")

    return create_pandas_tool(
        df=st.session_state.df_db,
        llm=st.session_state.llm,
    )