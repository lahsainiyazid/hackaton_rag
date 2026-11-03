
import os
import json

from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

load_dotenv()

# MongoDB
client = MongoClient(os.environ["MONGODB_URI"])
collection = client["tractor_rag"]["eco_agent"]

# Embedding model
model = SentenceTransformer("intfloat/multilingual-e5-small")

try:
    # Load JSON
    with open("/home/yazid/backend/eco_agent/data/complete_agent.json", "r", encoding="utf-8") as file:
        chunks = json.load(file)

    # Extract content
    texts = [chunk["Content"] for chunk in chunks]

    # Generate embeddings
    embeddings = model.encode(
        [f"passage: {text}" for text in texts],
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    # Prepare MongoDB documents
    documents = []

    for chunk, embedding in zip(chunks, embeddings):
        documents.append({
            "text": chunk["Content"],
            "metadata": chunk["metadata"],
            "embedding": embedding.tolist(),
        })

    # Insert documents
    if documents:
        collection.insert_many(documents)

    print(f"Successfully inserted {len(documents)} chunks!")

finally:
    client.close()
