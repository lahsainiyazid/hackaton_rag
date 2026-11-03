from typing import TypedDict 
from langchain_core.documents import Document 

class AgentState(TypedDict):
    question:str 
    expanded_query:str 
    documents:list[Document]
    products:list[dict[str,str]]
    context:str 
    answer:str
    recommendation:str
    financial_plan:str
