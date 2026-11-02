import os
from pymongo import MongoClient
from dotenv import load_dotenv,find_dotenv 

_=load_dotenv(find_dotenv())

client = MongoClient(os.getenv("MONGODB_URI"))

db = client["tractor_rag"]

collection = db.create_collection("eco_chunks")

print("Collection created!")
