from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

router_llm = Ollama(model="qwen3:8b")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a routing agent.

Your job:
- If the input is about SQL, SELECT, INSERT, databases → choose: SQL
- If the input is about charts, dataframe, plot, bar chart → choose: CHART
- Else → choose: CHAT

ONLY respond with one of these exact labels:
SQL
CHART
CHAT
        """
    ),
    ("human", "{input}")
])


def router_node(state):
    """Routes user message to SQL, CHART, or CHAT nodes."""

    # 1. Run the router LLM
    raw = router_llm.invoke(prompt.format(input=state["input"])).strip()

    # 2. Clean <think> tags if present
    clean = (
        raw.replace("<think>", "")
        .replace("</think>", "")
        .strip()
    )

    # 3. Detect correct route regardless of LLM verbosity
    clean_upper = clean.upper()

    if "SQL" in clean_upper:
        decision = "SQL"
    elif "CHART" in clean_upper or "PLOT" in clean_upper or "GRAPH" in clean_upper:
        decision = "CHART"
    else:
        decision = "CHAT"

    # 4. Return exact label for graph routing
    return {"route": decision}