from langchain_community.llms.ollama import Ollama

chat_llm = Ollama(model="mistral:7b-instruct-q4_K_M")

def chat_node(state):
    out = chat_llm.invoke(state["input"])
    return {"output": out}
