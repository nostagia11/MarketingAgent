import streamlit as st
from langchain_community.utilities import SQLDatabase

from langchain_ollama import OllamaLLM
from langchain.chains import create_sql_query_chain



# Create DB connection via SQLAlchemy
@st.cache_resource
def init_db():
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
SQLquery_chain = create_sql_query_chain(llm, db)
