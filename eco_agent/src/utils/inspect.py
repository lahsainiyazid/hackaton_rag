import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.environ["MONGODB_URI"])

db = client["tractor_rag"]
collection = db["agent_eco"]

print("Database:", db.name)
print("Collection:", collection.name)
print("Total documents:", collection.count_documents({}))

for doc in collection.find({}).limit(3):
    print("\nDOCUMENT:")
    for key, value in doc.items():
        if key == "embedding":
            print(key, ":", f"Vector with {len(value)} dimensions")
        else:
            print(key, ":", str(value)[:300])

client.close()
