from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Try connecting to MongoDB
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    client.admin.command('ping')
    db = client["todo_db"]
    print("SUCCESS: Connected to MongoDB Atlas")
except Exception as e:
    print(f"ERROR: Connection to MongoDB Atlas failed: {e}")
    raise e

users_collection = db["users"]
tasks_collection = db["tasks"]

# print("Collections:", db.list_collection_names())  # Debug
