from langchain_chroma import Chroma
from langchain_ollama import  OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA

from app.rag.get_embeddings import get_embedding_function

# Load Chroma index
embedding_function = get_embedding_function() # same function you used when populating the DB
db = Chroma(persist_directory="chroma_store", embedding_function=embedding_function)

# Turn into retriever
retriever = db.as_retriever(search_kwargs={"k": 3})

# Define prompt
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}

Question: {question}

If you don't know, say "I don't know".
"""
prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

# Initialize LLM
llm = OllamaLLM(model="qwen3:8b")

# Build RAG chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True,
)
