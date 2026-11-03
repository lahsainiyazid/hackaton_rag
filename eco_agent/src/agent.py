from src.utils.nodes import retrieval,scrape_bourse_agro,recommendation
from src.utils.objects import AgentState
from langgraph.graph  import StateGraph,START,END 
from dotenv import load_dotenv,find_dotenv 
_=load_dotenv(find_dotenv())

#We create here our graph object
builder=StateGraph(AgentState)
#Here we have our nodes:
builder.add_node("retrieval",retrieval)
builder.add_node("bourse_agro",scrape_bourse_agro)
builder.add_node("recommendation",recommendation)
builder.add_edge(START,"retrieval")
builder.add_edge("retrieval","bourse_agro")
builder.add_edge("bourse_agro","recommendation")
builder.add_edge("recommendation",END)

graph=builder.compile()
