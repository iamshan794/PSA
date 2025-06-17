FROM ubuntu:latest

# Install Python, Node.js, npm, git, and MongoDB in one layer for efficiency
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl git wget gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    # Install MongoDB
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add - && \
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org && \
    rm -rf /var/lib/apt/lists/*

# Verify installations
RUN python3 --version && pip --version && node --version && npm --version && mongod --version

WORKDIR /workspace

# Copy application files
COPY . /workspace 

# Clone the clarity-ai repository
RUN git clone https://github.com/mckaywrigley/clarity-ai.git

# Install Python dependencies
RUN pip install --no-cache --break-system-packages -r requirements.txt

# Install Node.js dependencies (if you have package.json)
# RUN npm install

# Create MongoDB data directory
RUN mkdir -p /data/db

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Start MongoDB in background\n\
echo "Starting MongoDB..."\n\
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log\n\
\n\
# Wait for MongoDB to start\n\
sleep 10\n\
\n\
# Initialize replica set\n\
echo "Initializing MongoDB replica set..."\n\
mongosh --eval "rs.initiate()" || echo "Replica set already initialized"\n\
\n\
# Start API server in background\n\
echo "Starting ADK API server..."\n\
adk api_server --host=0.0.0.0 --port=8000 &\n\
API_PID=$!\n\
\n\
# Wait for API server to start\n\
sleep 10\n\
\n\
# Start Streamlit app\n\
echo "Starting Streamlit app..."\n\
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=8501 &\n\
STREAMLIT_PID=$!\n\
\n\
# Wait for any process to exit\n\
wait $API_PID $STREAMLIT_PID\n\
' > /workspace/start.sh && chmod +x /workspace/start.sh

# Expose the ports your application uses
EXPOSE 8000 8501 8051

# Health check to ensure services are running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Use the startup script
CMD ["/workspace/start.sh"]