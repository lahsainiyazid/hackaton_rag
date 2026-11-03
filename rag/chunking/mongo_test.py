import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))

try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")

    db = client["RAGTRACTOR"]
    collection = db["chunks"]

    collection.insert_one({"message": "Hello MongoDB!"})
    print("Document inserted successfully!")

    print("Documents:", list(collection.find({}, {"_id": 0})))

finally:
    client.close()
