import os 
from objects import AgentState
from model import llm
from prompts.expansion import expansion_prompt
from prompts.answer import answer_prompt
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage,SystemMessage
from dotenv import load_dotenv,find_dotenv

_=load_dotenv(find_dotenv())


def retrieval(state:AgentState):
    MONGODB_URI=os.getenv("MONGODB_URI")
    client=MongoClient(MONGODB_URI)
    db=client["tractor_rag"]
    collection=db["agent_eco"]
    vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings,              
    index_name="vector_index",      
    text_key="Content",         
    embedding_key="embedding"       
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
    dense=vector_store.as_retriever(search_kwars={"k":5})
    hybrid=EnsembleRetriever(retrievers=[dense,sparse],weights=[0.4,0.6])


    expansion_call=expansion_llm.invoke([HumanMessage(content=request.question),SystemMessage(content=expansion_prompt)])
    expanded_query=expansion_call.content.strip()
    results=hybrid.invoke(expanded_query)
    pairs = [(request.question, doc.page_content) for doc in results]
    scores = reranker.predict(pairs)
    ranked_docs = [doc for _, doc in sorted(zip(scores, results), key=lambda x: x[0], reverse=True)]
    final_docs = ranked_docs[:5]
    formatted_prompt=answer_prompt.format(question=request.question,
                         expanded_query=expanded_query,
                         context=final_docs)
    answer=answer_llm.invoke([SystemMessage(content=formatted_prompt),HumanMessage(content=request.question)]).content.strip()
 

