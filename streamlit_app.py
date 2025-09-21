import streamlit as st

from app.rag.rag import rag_chain
from analysis.chat_with_dataset import build_dataset_agent
import pandas as pd
from langchain_ollama import OllamaLLM
from langchain.agents import initialize_agent, AgentType, Tool

st.set_page_config(page_title="Marketing app", layout="wide")
#st.title('Chat with dataset')

#uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])


#if uploaded_file is not None:
# Load CSV into DataFrame
#  df = pd.read_csv(uploaded_file)
#  with st.expander("Dataframe preview"):
#      st.write(df.tail(10))


#query = st.text_area("chat with dataframe")
container = st.container()
agent = None


# Define safe functions
def describe_data(query: str) -> str:
    return str(df.describe())


def preview_data(query: str) -> str:
    return str(df.head())

    #if query:

    # Define your tools for LangChain
    tools = [
        #Tool(
        #  name="chat_with_dataset",
        #  func=lambda q: build_dataset_agent(df).run(q),  # dataset_query_engine must expose a .query method
        # description="Chat with dataset"
        #),

        Tool(
            name="RAG_QA",
            func=lambda q: rag_chain.invoke(q)["result"],  # only return the answer
            description="Use this tool to answer questions based on the indexed documents."
        ),
        #Tool(
        #   name="Describe Data",
        #   func=describe_data,
        #  description="Get statistical summary of the dataset."
        #),
        #Tool(
        #   name="Preview Data",
        #  func=preview_data,
        # description="Show first 5 rows of the dataset."
        #)
    ]

    # Initialize LLM
    llm = OllamaLLM(model="qwen3:8b")

    # Create a ReAct agent with tools
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # ReAct-like behavior
        verbose=True
    )


#if st.button("Submit"):
#   if agent is not None and query:
#      with st.spinner("Agent thinking..."):
#         response = agent.run(query)  # use .run() not .query()
#         st.markdown("### 🤖 Agent Response")
#        st.write(response)
#elif agent is None:
#    st.warning("⚠️ Please upload a CSV file first.")
#elif not query:
#   st.warning("⚠️ Please enter a query before submitting.")


#----------
#rag_page = st.Page(
#   "app/rag/Pdf_rag.py",
#    title="Retrieval Augmented Generation (RAG)",
#   icon=":material/database:",
#)
#analysis = st.Page(
#   "app/chartgeneration/chat_with_dataset.py", title="chat with dataset", icon=":material/quick_reference:"
#)
chart_generation = st.Page(
    "chartgeneration/chart_generation.py", title="generate charts from dataset", icon=":material/quick_reference:"
)
Chat_with_db = st.Page("pages/front_query_db.py", title="chat with DB",
                       )

Marketing_Assistant = st.Page("pages/AI_Agent.py", title="Marketing assistant",
                              )
login = st.Page("pages/registerlogin.py", title="Register")

selected_page = st.navigation(
    {
        #"Login": [login],
        "GenAI": [Marketing_Assistant],
        "Tools for GenAI": [chart_generation, Chat_with_db],
        #"Agentic RAG": [
        #   rag_page
        #],

    },
    position="top",
)

selected_page.run()
