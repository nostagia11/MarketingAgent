from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.router import router_node
from graph.nodes.sql_node import sql_node
from graph.nodes.chart_node import chart_node
from graph.nodes.chat_node import chat_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("SQL", sql_node)
    graph.add_node("CHART", chart_node)
    graph.add_node("CHAT", chat_node)

    graph.set_entry_point("router")

    # Router → one of the tools
    graph.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "SQL": "SQL",
            "CHART": "CHART",
            "CHAT": "CHAT",
        }
    )

    graph.add_edge("SQL", END)
    graph.add_edge("CHART", END)
    graph.add_edge("CHAT", END)

    graph_agent = graph.compile()

    return graph_agent
