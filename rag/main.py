from fastapi import FastAPI 
import os 
from retrieval.objects import QuestionRequest
from models.models import expansion_llm,answer_llm,embeddings,reranker
from prompts.expansion import expansion_prompt
from prompts.answer import answer_prompt
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage,SystemMessage
from dotenv import load_dotenv,find_dotenv
from retrieval.retrieval import ask_rag_question 

_=load_dotenv(find_dotenv())
MONGODB_URI=os.getenv("MONGODB_URI")
client=MongoClient(MONGODB_URI)
db=client["tractor_rag"]
collection=db["chunks"]
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,              # Your HuggingFaceEmbeddings instance
    index_name="vector_index",         # Name of your Atlas Vector Search index
    text_key="Content",                  # Document field containing the text chunk
    embedding_key="embedding"          # Document field containing the vector
)
# We continue by loading our docs:
try:
    docs=[]
    results=collection.find({})
    for result in results:
        docs.append(result)
except Exception as e:
    print(f"Error{e}")
documents=[Document(
    page_content=record["text"],
    metadata={
        **record["metadata"],
        "chunk_id": record["metadata"]["id"]
    }) for record in docs]

sparse=BM25Retriever.from_documents(documents,
                                            k=5)
dense=vector_store.as_retriever(search_kwargs={"k":5})
hybrid=EnsembleRetriever(retrievers=[dense,sparse],weights=[0.4,0.6])


app=FastAPI()
@app.get("/")
def home():
    return {"Hackaton_rag_running":"True"}
@app.post("/ask")
def ask_question(request:QuestionRequest):
    return ask_rag_question(request)
