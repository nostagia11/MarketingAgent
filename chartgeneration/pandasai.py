import streamlit as st
from langchain_community.llms.ollama import Ollama
from pandasai.responses import ResponseParser

from data import load_data
import os
import pandas as pd



from pandasai import SmartDataframe

#from pandasai.callbacks import BaseCallback
#from pandasai.responses.response_parser import ResponseParser


class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
      st.dataframe(result["value"])
      return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return


"""class StreamlitCallback(BaseCallback):
    def __init__(self, container) ->None:
        Initialize callback handler
        self.container = container
    def on_code(self, response: str):
        self.container.code(response)"""

st.write("chat with dataset")


uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander("Dataframe preview"):
        st.write(df.tail(10))

else:
    st.warning("Please upload a CSV file.")




query = st.text_area("chat with dataframe")
container = st.container()

# Load your dataset
#df = pd.read_csv("your_dataset.csv")


if query:
    llm = Ollama(model="qwen3:8b")

    # SmartDataframe with Qwen3
    query_engine = SmartDataframe(df, config = {
        "llm": llm,
        "response_parser" : StreamlitResponse,
        "verbose": True,       # prints code + steps
        "save_logs": True,
    }, )

    answer = query_engine.chat(query)
    st.write(answer)