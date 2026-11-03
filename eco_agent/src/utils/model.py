from langchain_groq import ChatGroq 
from dotenv import load_dotenv,find_dotenv


_=load_dotenv(find_dotenv())

llm=ChatGroq(model="openai/gpt-oss-120b",temperature=0)
