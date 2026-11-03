from src.utils.nodes import retrieval,scrape_bourse_agro,recommendation,send_recommendation,send_financial_and_plan
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
builder.add_node("send_recommendation",send_recommendation)
builder.add_node("send_financial_plan",send_financial_and_plan)
builder.add_edge(START,"retrieval")
builder.add_edge("retrieval","bourse_agro")
builder.add_edge("bourse_agro","recommendation")
builder.add_edge("recommendation","send_recommendation")
builder.add_edge("send_recommendation","send_financial_plan")
builder.add_edge("send_financial_plan",END)

graph=builder.compile()
