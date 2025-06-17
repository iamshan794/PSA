#!/bin/bash
set -e
# Start MongoDB in background
echo "Starting MongoDB..."
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log

# Wait for MongoDB to start
sleep 10

# Initialize replica set
echo "Initializing MongoDB replica set..."
mongosh --eval "rs.initiate()" || echo "Replica set already initialized"

# Start API server in background
echo "Starting ADK API server..."
adk api_server --host=0.0.0.0 --port=8000 &
API_PID=$!

# Wait for API server to start
sleep 10

# Start Streamlit app
echo "Starting Streamlit app..."
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 &
STREAMLIT_PID=$!

# Wait for any process to exit
wait $API_PID $STREAMLIT_PID
