FROM ubuntu:latest

# Install Python, Node.js, npm, and git in one layer for efficiency
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl git && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Verify installations
RUN python3 --version && pip --version && node --version && npm --version

WORKDIR /workspace

COPY . /workspace 

RUN git clone https://github.com/mckaywrigley/clarity-ai.git

# Install Python dependencies
RUN pip install --no-cache --break-system-packages -r requirements.txt

# Install Node.js dependencies (if you have package.json)
# RUN npm install

CMD ["tail", "-f", "/dev/null"]