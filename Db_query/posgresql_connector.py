"""import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Database Connector", layout="centered")

# Keep connection state
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False
if "engine" not in st.session_state:
    st.session_state.engine = None

st.title("🔌 Database Connector")
with st.sidebar:
    st.write("🗄️ Configure PostgreSQL Connection")
    # Step 1: Select DB type
    db_type = st.selectbox("Select Database", ["PostgreSQL"])

    if db_type == "PostgreSQL":

        host = st.text_input("Host", placeholder="localhost")
        port = st.text_input("Port", value="5432")
        dbname = st.text_input("Database Name")
        user = st.text_input("User")
        password = st.text_input("Password", type="password")

        connect_btn = st.button("Connect")

        if connect_btn:
            try:
                uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
                engine = create_engine(uri)
                # Test connection
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                st.success("✅ Connection successful!")
                st.session_state.db_connected = True
                st.session_state.engine = engine
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

# Step 2: Query Section (only if connected)
if st.session_state.db_connected:
    st.divider()
    st.subheader("💬 Query the Database")

    query = st.text_area("Enter SQL query:")
    run_query = st.button("Run Query")

    if run_query and query:
        try:
            with st.session_state.engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = result.keys()
                st.dataframe(rows, use_container_width=True)
        except Exception as e:
            st.error(f"Error executing query: {e}")"""
#
#from langchain.tools import Tool
#from Db_query.connector import init_sql_chain
import streamlit as st
# db_query_chain.py
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from langchain_ollama import OllamaLLM
from langchain.chains import create_sql_query_chain
import streamlit as st
from sqlalchemy import text, create_engine


def init_sql_chain():
    """Create the SQL generation chain after DB connection."""

    if "db_connected" not in st.session_state:
        st.session_state.db_connected = True

    # Initialize engine once
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://user:pass@host:port/dbname")

    db = SQLDatabase(engine=st.session_state.engine)
    llm = OllamaLLM(model="qwen3:8b")
    return create_sql_query_chain(llm, db)

@tool
def run_sql_tool(query: str) -> str:
    """Tool: generate SQL with LLM, then execute it with SQLAlchemy 2.0."""

    # Ensure chain is initialized
    sql_chain = init_sql_chain()
    if sql_chain is None:
        return "❌ Database not connected."

    try:
        # 1. Generate SQL query from natural language
        sql_query = sql_chain.invoke({"question": query})
        if isinstance(sql_query, dict) and "result" in sql_query:
            sql_query = sql_query["result"]

        # Ensure we print the SQL for debugging
        print("Generated SQL:", sql_query)

        # 2. Execute SQL using SQLAlchemy 2.0
        engine = st.session_state.engine
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

        # Return rows in nice format
        return {
            "sql": sql_query,
            "columns": list(columns),
            "rows": rows
        }

    except Exception as e:
        return f"❌ SQL execution error: {e}"



