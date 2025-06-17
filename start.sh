#!/bin/bash

echo "Starting MongoDB..."
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log


sleep 10


echo "Initializing MongoDB replica set..."
mongosh --eval "rs.initiate()" || echo "Replica set already initialized"


echo "Starting ADK API server..."
adk api_server --host=0.0.0.0 --port=8000 &
API_PID=$!


sleep 10


echo "Starting Streamlit app..."
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 &
STREAMLIT_PID=$!


wait $API_PID $STREAMLIT_PID
