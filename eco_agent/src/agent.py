from src.utils.nodes import retrieval
from src.utils.objects import AgentState
from langgraph.graph  import StateGraph,START,END 
from dotenv import load_dotenv,find_dotenv 
_=load_dotenv(find_dotenv())

#We create here our graph object
builder=StateGraph(AgentState)
#Here we have our nodes:
builder.add_node("retrieval",retrieval)

builder.add_edge(START,"retrieval")
builder.add_edge("retrieval",END)

graph=builder.compile()
