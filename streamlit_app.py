import streamlit as st
import uuid
import requests
from pymongo import MongoClient
from datetime import datetime
import time
from bson import ObjectId
from multi_tool_agent.utils.ping_mongodb import watch_new_inserts 
import threading
import os 
from streamlit_autorefresh import st_autorefresh
import subprocess
import logging 

logging.basicConfig(
    level=logging.INFO,
    filename=f"{__file__}.log",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
# ---------- Session Setup ----------
st.set_page_config(layout="wide")

if "latest_product_doc" not in st.session_state:
    st.session_state.latest_product_doc = None

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

USER_ID = st.session_state.user_id
SESSION_ID = st.session_state.session_id
APP_NAME = "multi_tool_agent"

# ---------- MongoDB Setup ----------
MONGODB_URI = os.environ["MONGODB_URI"]
DB_NAME = "shopping_app"
COLLECTION_NAME = "api_results_raw"

#Event listener
if "watcher_started" not in st.session_state:
    threading.Thread(
        target=watch_new_inserts,
        args=(MONGODB_URI, DB_NAME, COLLECTION_NAME),
        daemon=True
    ).start()
    st.session_state.watcher_started = True

client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# ---------- Chat API Request (Mock) ----------
def initialize_sesion(app_name,user_id,session_id):
    url = f"http://127.0.0.1:8000"  # Replace with your FastAPI endpoint
    full_url = f"{url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
    payload = {"additionalProp1": {}}
    headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}   
    try:
        response = requests.post(full_url, headers=headers, json=payload)
        if response.status_code == 200 and response.ok:
            return (f"Session initialized successfully for app {app_name}, user {user_id}, session {session_id}")
        else:
            return (f"Failed to initialize session: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError as e:
        return (f"Failed to connect to service: Connection refused. Is the service running on the target host/port? Error: {str(e)}")
    except requests.exceptions.RequestException as e:
        return (f"Request failed: {str(e)}")
    except Exception as e:
        return (f"Unexpected error during session initialization: {str(e)}")

def get_chatbot_response(user_input,app_name,user_id,session_id):
    # Replace with real endpoint
    url = f"http://127.0.0.1:8000/run"  # Replace with your FastAPI endpoint
    allowable_agents = ["product_identifier_agent", "query_param_optimizer"]
    payload = { "appName": app_name,
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{
                    "text": user_input,
                    }]
                }
               }
    headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}   
    initialize_response = initialize_sesion(app_name,user_id,session_id)

    try:  
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for 4xx/5xx
        results = response.json()
        with open("response.json", "w") as f:
            import json
            json.dump(results, f, indent=4)
        returnable_results=[]
        for result_i in results:
            if result_i["author"] not in allowable_agents:
                continue
            for result_i_j in result_i["content"]["parts"]:
                if "text" in result_i_j.keys():
                    result = result_i_j["text"]
                    logger.info(f"User input: {user_input}")
                    logger.info(f"Chatbot response: {results}")
                    result = initialize_response + result
                    returnable_results.append(result)

        return returnable_results
                    
    
    except requests.exceptions.RequestException as e:
        return [f"{initialize_response}Request failed: {repr(e)}"]
    except Exception as e:
        return [f"{initialize_response}An error occurred while processing your request.{repr(e)}"]

# ---------- Streamlit Layout ----------

left_col, right_col = st.columns([2, 1])
right_placeholder = right_col.empty()

# 🧠 Sample condition to update right column
if "last_product_time" not in st.session_state:
    st.session_state.last_product_time = time.time()

# 🧠 Real check for new MongoDB product document
if "last_seen_object_id" not in st.session_state:
    # Initialize on first run
    latest_doc = collection.find_one(sort=[("_id", -1)])
    if latest_doc:
        st.session_state.last_seen_object_id = latest_doc["_id"]
        st.session_state.latest_product_doc = latest_doc
else:
    # Poll for new insert
    latest_doc = collection.find_one(sort=[("_id", -1)])
    if latest_doc and latest_doc["_id"] != st.session_state.last_seen_object_id:
        st.session_state.last_seen_object_id = latest_doc["_id"]
        st.session_state.latest_product_doc = latest_doc
        st.session_state.last_product_time = time.time()  # Update time if needed

# ---------- Left Panel: Chat ----------
with left_col:
    st.title("🛍️ Personal Shopping Assistant")
    for msg in st.session_state.chat_history:
        role = "🤖" if msg['role'] == 'bot' else "🧑"
        st.markdown(f"**{role}**: {msg['content']}")

    user_input = st.chat_input("Type your message...")
    if user_input:
        # User message
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Bot response
        for bot_response in get_chatbot_response(user_input,APP_NAME,USER_ID,SESSION_ID):
            st.session_state.chat_history.append({"role": "bot", "content": bot_response})
        st.rerun()  # Refresh display

# ---------- Right Panel: Product Card ----------
with right_placeholder.container():
    st.title("🛍️ Product Listings")
    if st.session_state.latest_product_doc:
        latest_product = st.session_state.latest_product_doc
        #latest_product=fetch_latest_product() 
        products=None
        try:
            products = latest_product["data"]["products"] 
        except KeyError:
            st.error("No products found in the latest document.")
            products = []

        if products:
            for product in products:
                with st.container():
                    # Image
                    image_url = product.get("product_photos", [""])[0]
                    if image_url:
                        st.image(image_url, width=200)

                    # Title
                    st.subheader(product.get("product_title", "No Title"))

                    # Description
                    st.caption(product.get("product_description", "No Description"))

                    # Rating
                    rating = product.get("product_rating", "N/A")
                    num_reviews = product.get("product_num_reviews", 0)
                    st.markdown(f"⭐ **{rating}** ({num_reviews} reviews)")

                    # Price
                    price = product.get("typical_price_range", "N/A")
                    st.markdown(f"💰 **{price}**")

                    # Link
                    url = product.get("product_page_url", "#")
                    st.markdown(f"[🔗 View Product]({url})")

                    st.markdown("---")
