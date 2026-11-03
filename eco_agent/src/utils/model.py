from langchain_groq import ChatGroq 
from dotenv import load_dotenv,find_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

_=load_dotenv(find_dotenv())

llm=ChatGroq(model="openai/gpt-oss-120b",temperature=0)
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

reranker = CrossEncoder("BAAI/bge-reranker-base")
