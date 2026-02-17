#!/bin/bash
echo "=== Tuankth's Assistant: Fixing n8n Environment ==="

# 1. Stop any running n8n processes (Host or Docker)
echo "[1/4] Stopping existing n8n instances..."
lsof -ti:5678 | xargs kill -9 2>/dev/null
docker rm -f n8n 2>/dev/null

# 2. Start n8n in Docker (This is the most reliable method)
echo "[2/4] Starting n8n container..."
# Use host networking for simplicity if on Linux, but for Mac -p is better.
# We mount a volume to persist data.
docker run -d --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_HOST=0.0.0.0 \
  -e N8N_PORT=5678 \
  -e WEBHOOK_URL=http://localhost:5678/ \
  docker.n8n.io/n8nio/n8n

# 3. Wait for startup
echo "[3/4] Waiting 20 seconds for n8n to initialize..."
sleep 20

# 4. Verify
echo "[4/4] Verification:"
if lsof -i :5678 >/dev/null; then
    echo "✅ n8n is LISTENING on port 5678."
    echo "You can now ask the Agent to continue configuration."
else
    echo "❌ n8n failed to start. Please check 'docker logs n8n'."
fi
