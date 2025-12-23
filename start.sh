#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Function to kill process on a port
kill_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo "Killing process on port $PORT (PID: $PID)..."
        kill -9 $PID
    fi
}

# Cleanup old processes
echo "Cleaning up old processes..."
if command -v lsof >/dev/null; then
    kill_port 8000
    kill_port 8501
else
    echo "Warning: 'lsof' not found, skipping port cleanup."
fi

# Start Backend
echo "Starting FastAPI Backend..."
python backend/main.py &
BACKEND_PID=$!

# Wait for backend to be ready (simple sleep for now)
sleep 2

# Start Frontend
echo "Starting Streamlit Frontend..."
streamlit run frontend/app.py &
FRONTEND_PID=$!

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

echo "Both services are running. Press Ctrl+C to stop."
wait
