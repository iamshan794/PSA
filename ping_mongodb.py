import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Generator
import sys
from bson import ObjectId
def connect_to_mongodb(uri="mongodb://mongodb:27017/", db_name="test_db", collection_name="test_collection"):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("✅ Successfully connected to MongoDB!")
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except ConnectionFailure as e:
        print("❌ MongoDB connection failed:", e)
        return None

def insert_json_data(collection, json_path: str):
    with open(json_path, "r") as file:
        data = json.load(file)
        # Insert one or many depending on type
        if isinstance(data, list):
            result = collection.insert_many(data)
            print(f"✅ Inserted {len(result.inserted_ids)} documents.")
        else:
            result = collection.insert_one(data)
            print(f"✅ Inserted 1 document with _id: {result.inserted_id}")

def retrieve_all_documents(collection) -> Generator[dict, None, None]:
    cursor = collection.find({})
    for document in cursor:
        yield document

if __name__ == "__main__":
    # Change these if needed
    if sys.argv[1] == "insert":
        JSON_FILE_PATH = "/workspace/assets/outputs/product_search_results_laptop.json"
        DB_NAME = "shopping_app"
        COLLECTION_NAME = "api_results_raw"

        collection = connect_to_mongodb(db_name=DB_NAME, collection_name=COLLECTION_NAME)
        
        if collection is not None:
            insert_json_data(collection, JSON_FILE_PATH)

            print("📄 Retrieving documents:")
            for doc in retrieve_all_documents(collection):
                print(doc)
    elif sys.argv[1] == "ping":
        DB_NAME = "shopping_app"
        COLLECTION_NAME = "api_results_raw"
        collection = connect_to_mongodb(db_name=DB_NAME, collection_name=COLLECTION_NAME)
        try:
            doc = collection.find_one({"_id": ObjectId("6845ee9924abea9785b9accc")})
            print(doc)
        except Exception as e:
            print(f"Error retrieving document: {e}")
            exit()
        for doc in retrieve_all_documents(collection):
            print(doc)