import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Generator
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
import os 

DB_NAME = "shopping_app"
COLLECTION_NAME = "api_results_raw"
MONGO_URI = os.environ["MONGODB_URI"]

def watch_new_inserts(uri: str, db_name: str, collection_name: str):
    client = MongoClient(uri)
    collection = client[db_name][collection_name]
    
    print("🔍 Listening for new documents...")

    with collection.watch([{"$match": {"operationType": "insert"}}]) as stream:
        for change in stream:
            latest_id = change["fullDocument"]["_id"]
            print(f"🆕 New document inserted with _id: {latest_id}")

def connect_to_mongodb(uri=MONGO_URI, db_name="test_db", collection_name="test_collection"):
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

def insert_json_data(collection, json_path: str,direct_json=False):
    if not direct_json:
        with open(json_path, "r") as file:
            data = json.load(file)
    else:
        data = json_path
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

def agent_tool_insert_product(response_as_json:dict)->None:
    '''
    A tool that helps the agent to insert the 
    response_as_json: JSON response to be inserted.
    '''
    global DB_NAME, COLLECTION_NAME, MONGO_URI
    try:
        collection = connect_to_mongodb(db_name=DB_NAME, collection_name=COLLECTION_NAME)
        if collection is not None:
            
            insert_json_data(collection, response_as_json,direct_json=True)

    except Exception as e:
        print(f"❌ Error inserting document: {e}")


def get_mongodb_stats():
    return

if __name__ == "__main__":
    # Change these if needed
    if sys.argv[1] == "insert":
        JSON_FILE_PATH = "/workspace/assets/outputs/product_search_results_laptop.json"
        JSON_FILE_PATH = "/workspace/assets/outputs/gray welcome cotton doormat_20250607_200235.json"
        DB_NAME = "shopping_app"
        COLLECTION_NAME = "api_results_raw"

        collection = connect_to_mongodb(db_name=DB_NAME, collection_name=COLLECTION_NAME)
        
        if collection is not None:
            insert_json_data(collection, JSON_FILE_PATH)

            print("📄 Retrieving documents:")

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

    elif sys.argv[1] == "event_listener":
        DB_NAME = "shopping_app"
        COLLECTION_NAME = "api_results_raw"
        
        latest_id = watch_new_inserts(MONGO_URI, DB_NAME, COLLECTION_NAME)
        if latest_id:
            print(f"Latest document ID: {latest_id}")
        else:
            print("No documents found in the collection.")
    elif sys.argv[1] == "drop":
        DB_NAME = "shopping_app"
        COLLECTION_NAME = "api_results_raw"
        
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        result = collection.drop()
        print(f"✅ Collection '{COLLECTION_NAME}' dropped successfully.")
        