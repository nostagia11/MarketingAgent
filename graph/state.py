from dataclasses import dataclass
from typing import Dict, Any
from langgraph.graph import StateGraph, END
@dataclass
class AgentState(Dict):
    input: str
    output: str
    route: str
