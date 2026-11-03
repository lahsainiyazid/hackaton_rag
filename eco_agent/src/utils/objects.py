from typing import TypedDict 
from langchain_core.documents import Document 

class AgentState(TypedDict):
    question:str 
    expanded_query:str 
    documents:list[Document]
    context:str 
    answer:str 

