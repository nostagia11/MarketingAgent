from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import OllamaLLM





# Create the agent that can query pandas DataFrame


# If you want to give custom instructions like your old `instruction_str` and `new_prompt`,
# you can prepend them to the query instead of update_prompts.
#"""custom_instruction =
#You are an expert data analyst. Answer questions using the DataFrame provided.
#Use concise explanations and return results in a clean format.


#def query_dataset(question: str):
#    return dataset_query_engine.run(f"{custom_instruction}\n\nQuestion: {question}")

from langchain_experimental.agents import create_pandas_dataframe_agent


def build_dataset_agent(df):
    """
    Create an agent that can query the given pandas DataFrame.
    """
    # Initialize LLM
    llm = OllamaLLM(model="qwen3:8b") # or mistral, llama, etc.

    dataset_query_engine = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_type="openai-tools",
        allow_dangerous_code=True# behaves like ReAct agent

    )
    return dataset_query_engine
