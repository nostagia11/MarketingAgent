"""import pandas as pd

#from chartgeneration.pandas_wrapper import create_pandas_tool
from langchain_community.llms.ollama import Ollama
import streamlit as st
#from graph.build_graph import build_graph
#from tools.agent import AgentToolCall
#from tools.utils import strip_think

llm = Ollama(model="mistral:7b-instruct-q4_K_M")
#graph_agent = build_graph()

def chart_node(state):
    # Must have DB connection
    if "engine" not in st.session_state:
        return {"output": "❌ Database not connected. Connect first."}

    # Must have dataframe loaded
    if "df_db" not in st.session_state:
        return {"output": "❌ No DataFrame loaded from database."}

    pandas_tool = create_pandas_tool(st.session_state.df_db, llm)

    try:
        #response = graph_agent.run(state["input"])
        result = pandas_tool.run(state["input"])
        # Try to detect chart or text result
        if hasattr(result, "savefig"):  # Matplotlib figure
            st.pyplot(result)
            st.session_state["last_chart"] = result
        elif isinstance(result, pd.DataFrame):
            st.dataframe(result)
        else:
            st.write(result)

            # Display the text response from the agent
        st.markdown("### 🤖 Agent Response")
        st.write(result)

        # Store assistant reply in chat history
        st.session_state["messages"].append(
            {"role": "assistant", "content": str(result)}
        )
    except Exception as e:
        #return {"output": f"❌ Chart generation failed: {e}"}
        st.error(f"Error generating chart: {e}")
        st.session_state["messages"].append(
            {"role": "assistant", "content": f"⚠️ Error: {e}"}
        )"""
#|-----------------
""" clean = strip_think(str(raw))

        # 🔥 Handle all possible PandasAI outputs safely
        if isinstance(raw, tuple):
            # keep only the LAST element (actual chart or path)
            last = raw[-1]
            return {"output": str(last)}

        elif isinstance(raw, list):
            # If it's a list of chart paths, show first chart
            return {"output": str(raw[0])}

        elif isinstance(raw, dict):
            # PandasAI sometimes returns {"path": "..."}
            if "path" in raw:
                return {"output": raw["path"]}
            return {"output": str(raw)}

        else:
            # Default fallback — already cleaned
            return {"output": clean}"""
