from pymongo import MongoClient
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
collection = client["tractor_rag"]["agent_eco"]

print("Total MongoDB docs:", collection.count_documents({}))

raw_docs = list(collection.find({}, {"Content": 1, "metadata": 1}))

documents = [
    Document(
        page_content=d["Content"],
        metadata=d.get("metadata") or {}
    )
    for d in raw_docs
    if isinstance(d.get("Content"), str) and d["Content"].strip()
]

print("Valid documents:", len(documents))

if documents:
    bm25 = BM25Retriever.from_documents(documents)
    bm25.k = 3

    results = bm25.invoke("ما هي المحاصيل الزراعية الرئيسية في منطقة تيفلت؟")

    for result in results:
        print(result.page_content[:300])
else:
    print("No valid documents. Check MongoDB collection and Content field.")
