#!/bin/bash
# SHEtoken Agent Startup Script
# 1. Start Ollama server
# 2. Pull models if not cached
# 3. Run the agent
# 4. Exit (Cloud Run job ends)

set -e

echo "=== SHEtoken WEI Agent Starting ==="
echo "Time: $(date -u)"

# Start Ollama in background
echo "[1/4] Starting Ollama..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "[2/4] Waiting for Ollama..."
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  Ollama ready"
        break
    fi
    sleep 2
done

# Pull models (cached in Cloud Run if using persistent storage)
echo "[3/4] Checking models..."

if ! ollama list | grep -q "phi3.5"; then
    echo "  Pulling phi3.5 (~2.5GB)..."
    ollama pull phi3.5
fi

if ! ollama list | grep -q "qwen2.5:3b"; then
    echo "  Pulling qwen2.5:3b (~2GB)..."
    ollama pull qwen2.5:3b
fi

echo "  Models ready"

# Run the agent
echo "[4/4] Running WEI agent..."
python3 run_agent.py

echo "=== Agent complete ==="

# Stop Ollama
kill $OLLAMA_PID 2>/dev/null || true
