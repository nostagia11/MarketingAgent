import streamlit as st
import re

from langchain_core.prompts import PromptTemplate

from Db_query.db_query import SQLquery_chain
from Db_query.db_query import db


st.title("Chat with PostgreSQL Database")


def extract_sql(text):
    # This regex captures the first SQL statement starting with SELECT, INSERT, UPDATE, DELETE
    match = re.search(r"(SELECT .*?;|INSERT .*?;|UPDATE .*?;|DELETE .*?;)", text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1)
    else:
        # fallback if no match found
        return text

    # Form with Submit button


with st.form("query_form"):
    user_query = st.text_input("Ask me a question:")
    submitted = st.form_submit_button("Submit")

if submitted and user_query:
    # Step 1: Generate SQL
    #sql_query = query_chain.invoke({"question": user_query})
    #st.code(sql_query, language="sql")

    # Step 2: Execute SQL
    #try:
    #   result = db.run(sql_query)
    #  st.write("Result:", result)
    #except Exception as e:
    #   st.error(f"SQL execution failed: {e}")
    # Step 1: Generate SQL
    with st.spinner("Agent thinking..."):

        SQLprompt = f"""
           You are an SQL generator. 
           Return ONLY a valid SQL query, nothing else. 
           Do NOT include explanations, reasoning, or <think> tags.
           Use the following format:

                Question: "Question here"
                SQLQuery: "SQL Query to run"
                SQLResult: "Result of the SQLQuery"
                Answer: "Final answer here"


           Question: {user_query}
           """

        llm_output = SQLquery_chain.invoke({"question": SQLprompt})

        # Optional: print reasoning to terminal
        print("LLM raw output:\n", llm_output)

        # Step 2: Extract SQL only (assuming it ends with a semicolon)

        sql_query = extract_sql(llm_output)

        # Show the SQL in Streamlit
        st.code(sql_query, language="sql")

        # Step 3: Execute SQL safely
        try:
            result = db.run(sql_query)
            st.write("Result:", result)
        except Exception as e:
            st.error(f"SQL execution failed: {e}")
