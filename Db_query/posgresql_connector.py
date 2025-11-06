import streamlit as st
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
            st.error(f"Error executing query: {e}")
