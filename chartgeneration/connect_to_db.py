import pandas as pd
from langchain_community.utilities import SQLDatabase
import streamlit as st
from sqlalchemy import create_engine

from Db_query.connector import connect_to_postgresql

"""Creates the 'Connect to PostgreSQL' button + expander UI."""


def connect_to_db():
    with st.sidebar:
        if "db_connected" not in st.session_state:
            st.session_state.db_connected = False
        if "engine" not in st.session_state:
            st.session_state.engine = None
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

                if st.button("Connect", key="connect"):
                    try:
                        st.write("Connecting to the PostgreSQL database...")
                        uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
                        engine = create_engine(uri)

                        st.session_state.engine = engine
                        st.write("engine initialized...")
                        st.session_state.db_connected = True
                        #st.session_state.df = None
                        st.success("Connected successfully!")

                        # Initialize engine once
                        #if 'engine' not in st.session_state:
                        #   st.session_state.engine = create_engine("postgresql+psycopg2://user:pass@host:port/dbname")
                        st.write(st.session_state)
                    except Exception as e:
                        st.error(f"Connection failed: {e}")

        """if st.session_state.db_connected and st.session_state.engine is not None:

            #db = SQLDatabase(engine=st.session_state.engine)

            # ---- Load dataframe from DB after connecting ----
            try:
                engine = st.session_state.engine
                query = "SELECT * FROM marketing_campaign LIMIT 100"
                st.write("Running Query:", query)
                st.write("Engine:", st.session_state.engine)

                with engine.connect() as conn:
                    df = pd.read_sql(query, conn)

                st.write(type(df))

                st.session_state.df = df
                st.success("📄 Table loaded successfully!")

            except Exception as e:
                st.error(f"❌ Error loading table: {e}")"""
