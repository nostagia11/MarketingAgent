import argparse

from langchain_community.llms.ollama import Ollama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from app.rag.populate_db import get_embedding_function


CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="the query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    embedding_function = get_embedding_function()
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function
    )
    # lookup templates
    PROMPT_TEMPLATE = """
    Answer the question based only on the following context:
    {context}

    ---
    Answer the question based on the above context: {question}"""
   # prompt = PROMPT_TEMPLATE.from_template(
    """you are a helpful assistant. You will be provided with a query and a chat history.
    Your task is to retrieve relevent information from the vector store and provide a response .
    For this you use the tool 'retrieve' to get the relevent information.
    
    the query is as follows:
    {input}
    
    The chat history is as follows: 
    {chat_history}
    
    Please provide a concise and informative response based on the retrieved information.
    If you don't know the answer, say "I dont know" .
    
    You can use the scratchpad to store any intermediate results or notes.
    
    Th scratpad is as follows:
    {agent_scratchpad}
    
    return text as follows:
    <Answer to the question>
    
    """
    #)
    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    # lookup if u can adjust to mprofessionl tone to optimize
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)
    # text at this stage : see 5 chunks query +answer
    model = Ollama(model="mistral:7b-instruct-q4_K_M")
    response_text = model.invoke(prompt)
    print(response_text)

    # get original source of the text
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text



if __name__ == "__main__":
    main()