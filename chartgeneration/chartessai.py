import streamlit as st
import pandas as pd
from langchain_community.llms.ollama import Ollama

from pandasai import SmartDataframe
from pandasai.llm.openai import OpenAI
import uuid

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="PandasAI Chart Builder", layout="wide")

# ---------- SESSION STATE ----------
if "dashboard_charts" not in st.session_state:
    st.session_state["dashboard_charts"] = []

# ---------- SAMPLE DATA ----------
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    with st.expander("Dataframe preview"):
        st.write(df.tail(10))

else:
    st.warning("Please upload a CSV file.")


st.title("🤖 PandasAI Interactive Chart Builder")
st.write("Ask PandasAI to generate a chart from your dataset.")

# ---------- LLM INIT (Replace with your config) ----------
llm = Ollama(model="qwen3:8b")
smart_df = SmartDataframe(df, config={"llm": llm})

# ---------- USER PROMPT ----------
user_prompt = st.text_input("💬 Ask something (e.g., 'Plot sales vs month'):")

if st.button("Generate Chart"):
    with st.spinner("Generating chart..."):
        try:
            chart = smart_df.chat(user_prompt)
            st.session_state["last_chart"] = chart
            st.image(chart)
        except Exception as e:
            st.error(f"Error generating chart: {e}")

# ---------- ADD TO DASHBOARD ----------
if "last_chart" in st.session_state:
    if st.button("➕ Add to Dashboard"):
        chart_id = str(uuid.uuid4())
        st.session_state["dashboard_charts"].append({
            "id": chart_id,
            "title": user_prompt,
            "figure": st.image(st.session_state["last_chart"])
        })
        st.success("✅ Chart added to dashboard!")

st.page_link("chartgeneration/dashboard_builder.py", label="➡️ Go to Dashboard", icon="📊")
