

import os

from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.objects import AgentState
from src.utils.model import llm, embeddings, reranker
from src.utils.prompts.expansion_prompt import expansion_prompt
from src.utils.prompts.answer_prompt import answer_prompt


def retrieval(state: AgentState):
    question = state["question"]

    client = MongoClient(os.environ["MONGODB_URI"])
    try:
        collection = client["tractor_rag"]["agent_eco"]

        # Load documents for BM25
        records = list(collection.find({}))
        print("MongoDB records:", len(records))

        documents = [
            Document(
                page_content=record["Content"],
                metadata=record.get("metadata", {})
            )
            for record in records
            if record.get("Content")
        ]

        if not documents:
            raise ValueError("No valid documents found for BM25")

        # Dense retrieval
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="vector_index",
            text_key="Content",
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
            weights=[0.4, 0.6]
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
