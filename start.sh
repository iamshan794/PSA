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
<<<<<<< HEAD
exec streamlit run streamlit_app.py --server.address=$APP_HOST --server.port=${PORT:-8501} 
=======
exec streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} 

alias kill_fe="ps -aux | grep \"streamlit\" | awk 'NR==1 {print $2}' | xargs kill"
>>>>>>> b58a2a9 (Final Local hosted app)
