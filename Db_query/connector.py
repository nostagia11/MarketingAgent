import pandas as pd

#from langchain_community.utilities import SQLDatabase

#from langchain_ollama import OllamaLLM
#from langchain.chains import create_sql_query_chain



# Create DB connection via SQLAlchemy

"""def init_db():
    db_uri = (
        f"postgresql+psycopg2://{st.secrets['postgres']['user']}:{st.secrets['postgres']['password']}@"
        f"{st.secrets['postgres']['host']}:{st.secrets['postgres']['port']}/{st.secrets['postgres']['dbname']}"
    )
    return SQLDatabase.from_uri(db_uri)


db = init_db()

# Initialize LLM
#llm = OllamaLLM(model="qwen3:8b")
llm = OllamaLLM(model="mistral:7b-instruct-q4_K_M")
# Build the chain
#db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
SQLquery_chain = create_sql_query_chain(llm, db)"""
# connector.py
import streamlit as st
from sqlalchemy import create_engine, text




@st.cache_resource
def connect_to_postgresql(host, port, dbname, user, password):
    """Creates SQLAlchemy engine and tests the connection."""
    st.write("Connecting to the PostgreSQL database...")
    uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    engine = create_engine(uri)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    st.session_state.engine = engine
    st.write("engine initialized...")
    st.session_state.db_connected = True
    st.session_state.df_db = None

    # 🔥 LOAD DEFAULT TABLE INTO A DATAFRAME
    df_db = pd.read_sql("SELECT * FROM marketing_campaign LIMIT 500", engine)
    st.session_state.df_db = df_db
    return True

import streamlit as st



def pg_connection_widget():
    """Creates the 'Connect to PostgreSQL' button + expander UI."""

    with st.sidebar:
        st.subheader("🔌 Connect to Database")

        if st.button("Connect to PostgreSQL"):
            st.session_state.show_pg_expander = True

        if st.session_state.get("show_pg_expander", False):

            with st.expander("PostgreSQL Connection Settings", expanded=True):
                host = st.text_input("Host", value="localhost")
                port = st.text_input("Port", value="5432")
                dbname = st.text_input("Database Name")
                user = st.text_input("User")
                password = st.text_input("Password", type="password")

                if st.button("Connect",key="connect"):
                    try:
                        connect_to_postgresql(host, port, dbname, user, password)
                        st.success("Connected successfully!")
                        st.write(st.session_state)
                    except Exception as e:
                        st.error(f"Connection failed: {e}")
