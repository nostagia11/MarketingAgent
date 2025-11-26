import streamlit as st
#from tools.sql_tool import run_sql_tool
from Db_query.posgresql_connector import run_sql_tool
def sql_node(state):
    response = run_sql_tool(state["input"])
    return {"output": str(response)}
