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

# Install Python dependencies
RUN pip install --no-cache --break-system-packages -r requirements.txt

# Install Node.js dependencies (if you have package.json)
# RUN npm install

# Create MongoDB data directory
RUN mkdir -p /data/db

RUN chmod +x /workspace/start.sh

# Expose the ports your application uses
EXPOSE 8501

# Use the startup script
CMD ["/workspace/start.sh"]