import streamlit as st
import uuid
import requests
from pymongo import MongoClient
from datetime import datetime
import time
from bson import ObjectId
from ping_mongodb import watch_new_inserts 
import threading
import os 
from streamlit_autorefresh import st_autorefresh


st.set_page_config(layout="wide")
# 📦 Placeholder to dynamically update right column


# ---------- Session Setup ----------

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


if "watcher_started" not in st.session_state:
    threading.Thread(
        target=watch_new_inserts,
        args=(MONGODB_URI, DB_NAME, COLLECTION_NAME),
        daemon=True
    ).start()
    st.session_state.watcher_started = True

client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION_NAME]

def fetch_latest_product():
    doc = collection.find_one({"_id": ObjectId("684782732322bdd492e2a0f1")})
    return doc

# ---------- Chat API Request (Mock) ----------
def initialize_sesion(app_name,user_id,session_id):
    url = "http://0.0.0.0:8000"  # Replace with your FastAPI endpoint
    full_url = f"{url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
    payload = {"additionalProp1": {}}
    headers = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
    response = requests.post(full_url, headers=headers, json=payload, timeout=(10, 30))
    if response.status_code == 200 and response.ok:
        print(f"Session initialized successfully for app {app_name}, user {user_id}, session {session_id}")
    else:
        print(f"Failed to initialize session: {response.status_code} - {response.text}")
    
def list_apps():
    url = "http://0.0.0.0:8000/list-apps/"  # Replace with your FastAPI endpoint
    response = requests.get(url, timeout=30)
    #print("AT list apps",response.json())

def get_chatbot_response(user_input,app_name,user_id,session_id):
    list_apps()
    # Replace with real endpoint
    url = "http://0.0.0.0:8000/run"  # Replace with your FastAPI endpoint

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
    try:
        initialize_sesion(app_name,user_id,session_id)
        response = requests.post(url, headers=headers, json=payload, timeout=(10, 30))
        response.raise_for_status()  # Raises an error for 4xx/5xx
        result = response.json()
        result = result[0]["content"]["parts"][0]["text"]
        return result
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return f"Apologies, I am not reachable at the moment due to {e.response.status_code}:{e.response.text} and {e.response.headers}. Please try again later"
    except Exception as e:
        return "An error occurred while processing your request."

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
        bot_response = get_chatbot_response(user_input,APP_NAME,USER_ID,SESSION_ID)
        st.session_state.chat_history.append({"role": "bot", "content": bot_response})

        st.rerun()  # Refresh display

# ---------- Right Panel: Product Card ----------
with right_placeholder.container():
    st.title("🛍️ Product Listings")
    if st.session_state.latest_product_doc:
        latest_product = st.session_state.latest_product_doc
        #latest_product=fetch_latest_product()
        products = latest_product["data"]["products"] 
        
        if not products:
            st.info("No products available.")
        else:
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

