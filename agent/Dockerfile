# SHEtoken WEI News Agent — Dockerfile
# Runs Ollama (Phi-3.5 + Qwen2.5:3b) + Python agent on Cloud Run

FROM ollama/ollama:latest

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Copy startup script
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh

# Cloud Run requires PORT env var
ENV PORT=8080
ENV OLLAMA_HOST=http://localhost:11434

# Startup: launch Ollama, pull models, run agent
CMD ["/startup.sh"]
