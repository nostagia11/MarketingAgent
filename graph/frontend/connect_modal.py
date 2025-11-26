import pandas as pd
import streamlit as st
from Db_query.connector import connect_to_postgresql
#from Db_query.sql_chain_builder import init_sql_chain
from Db_query.posgresql_connector import init_sql_chain
def connection_sidebar():
    st.sidebar.header("🔌 PostgreSQL Connection")

    host = st.sidebar.text_input("Host", "localhost")
    port = st.sidebar.text_input("Port", "5432")
    dbname = st.sidebar.text_input("Database Name")
    user = st.sidebar.text_input("User")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Connect"):
        msg = connect_to_postgresql(host, port, dbname, user, password)
        st.sidebar.write(msg)

        if st.session_state.get("db_connected"):
            init_sql_chain()

            # ---- Load dataframe from DB after connecting ----
            try:
                engine = st.session_state.engine
                query = "SELECT * FROM marketing_campaign"  # ⬅️ or any table name

                with engine.connect() as conn:
                    df = pd.read_sql(query, conn)

                st.session_state.df = df
                st.success("📄 Table loaded successfully!")

            except Exception as e:
                st.error(f"❌ Error loading table: {e}")