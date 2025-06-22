FROM ubuntu:latest

# Install Python, Node.js, npm, git, and MongoDB
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

# Installation Verification
RUN python3 --version && pip --version && node --version && npm --version && mongod --version

WORKDIR /workspace
COPY . /workspace

#Environment variables

ARG ENV_CONTENT
ARG MONGODB_URI
ARG API_URL
ARG API_KEY
ARG API_HOST
ARG PROJECT_PATH
ARG FASTAPI_HOST
ARG APP_HOST

ENV MONGODB_URI=${MONGODB_URI}
ENV API_URL=${API_URL}
ENV API_KEY=${API_KEY}
ENV API_HOST=${API_HOST}
ENV PROJECT_PATH=${PROJECT_PATH}
ENV FASTAPI_HOST=0.0.0.0
ENV APP_HOST=0.0.0.0

RUN echo "$ENV_CONTENT" > multi_tool_agent/.env

# Install Python dependencies
RUN pip install --no-cache --break-system-packages -r requirements.txt

EXPOSE 8501

CMD ["sh", "-c", "\
set -e && \
echo 'Starting MongoDB...' && \
mongod --replSet rs0 --bind_ip_all --fork --logpath /var/log/mongodb.log && \
sleep 10 && \
echo 'Initializing MongoDB replica set...' && \
(mongosh --eval 'rs.initiate()' || echo 'Replica set already initialized') && \
echo 'Starting ADK API server...' && \
adk api_server --host=0.0.0.0 --port=8016 & \
sleep 20 && \
echo 'Starting Streamlit app...' && \
streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501} && \
wait"]
