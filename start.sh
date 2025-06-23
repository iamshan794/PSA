#!/bin/bash

echo "Starting MongoDB..."
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log


sleep 10


echo "Initializing MongoDB replica set..."
mongosh --eval "rs.initiate()" || echo "Replica set already initialized"


echo "Starting ADK API server..."
adk api_server --host=$FASTAPI_HOST --port=8000 &
API_PID=$!


sleep 10


echo "Starting Streamlit app..."

exec streamlit run streamlit_app.py --server.address=$APP_HOST --server.port=${PORT:-8501} 

