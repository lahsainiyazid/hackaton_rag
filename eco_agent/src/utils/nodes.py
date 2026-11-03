import os
import cloudscraper 
from dotenv import load_dotenv,find_dotenv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.objects import AgentState
from src.utils.model import llm, embeddings, reranker
from src.utils.prompts.expansion_prompt import expansion_prompt
from src.utils.prompts.recommendation_prompt import recommendation_prompt
from src.utils.prompts.answer_prompt import answer_prompt

_=load_dotenv(find_dotenv())

def retrieval(state: AgentState):
    question = state["question"]

    client = MongoClient(os.environ["MONGODB_URI"])
    try:
        collection = client["tractor_rag"]["eco_agent"]

        # Load documents for BM25
        records = list(collection.find({}))
        print("MongoDB records:", len(records))

        documents = [
            Document(
                page_content=record["text"],
                metadata=record.get("metadata", {})
            )
            for record in records
            if record.get("text")
        ]

        if not documents:
            raise ValueError("No valid documents found for BM25")

        # Dense retrieval
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="vector_index",
            text_key="text",
            embedding_key="embedding"
        )

        dense = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )

        # Sparse retrieval
        sparse = BM25Retriever.from_documents(
            documents,
            k=5
        )

        hybrid = EnsembleRetriever(
            retrievers=[dense, sparse],
            weights=[0.6, 0.4]
        )

        # Query expansion
        expansion_response = llm.invoke([
            SystemMessage(content=expansion_prompt),
            HumanMessage(content=question)
        ])

        expanded_query = expansion_response.content.strip()

        # Hybrid retrieval
        results = hybrid.invoke(expanded_query)

        # Reranking
        if results:
            pairs = [
                (question, doc.page_content)
                for doc in results
            ]

            scores = reranker.predict(pairs)

            ranked_docs = [
                doc for _, doc in sorted(
                    zip(scores, results),
                    key=lambda x: x[0],
                    reverse=True
                )
            ]
            final_docs = ranked_docs[:5]
        else:
            final_docs = []

        # Format context
        context = "\n\n".join(
            f"المصدر {i + 1}:\n{doc.page_content}"
            for i, doc in enumerate(final_docs)
        )

        # Generate answer
        formatted_prompt = answer_prompt.format(
            question=question,
            expanded_query=expanded_query,
            context=context
        )

        answer = llm.invoke([
            SystemMessage(content=formatted_prompt)
        ]).content.strip()

        return {
            "expanded_query": expanded_query,
            "documents": final_docs,
            "context": context,
            "answer": answer
        }

    finally:
        client.close()



def scrape_bourse_agro(state:AgentState)->list[dict[str,str]]:
    url="https://bourseagro.com/prix/casa"
    scraper=cloudscraper.create_scraper()
    response=scraper.get(url)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser")
    products=[]
    for row in soup.select("tr[data-nom][data-prix]"):
        products.append({
        "name": row["data-nom"],
        "category": row["data-cat"],
        "price": float(row["data-prix"])
    })
    return {
        "products":products
    }


def recommendation(state:AgentState)->str:
    question=state["question"]
    context=state["context"]
    products=state["products"]
    recom_prompt=recommendation_prompt.format(
   question=question,
        products=products,
        context=context)
    response=llm.invoke([HumanMessage(content="Generate an answer in arabic"),SystemMessage(content=recom_prompt)]).content.strip()

    return {"recommendation":response}

def send_recommendation(state:AgentState):

    """
    Here is a small python function to send recommendation 
    """
    recom=str(state.get("recommendation"))
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
    "chat_id": CHAT_ID,
    "text": recom}
    requests.post(url,json=payload)

