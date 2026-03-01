#!/bin/bash

# ITO Startup Script
# Starts both the server (docker compose) and the electron app

# Resolve symlinks to get the actual script location
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"

echo "Starting ITO..."

# Start the server in the background
echo "Starting server (docker compose)..."
cd "$SCRIPT_DIR/server"
docker compose up --build &
SERVER_PID=$!

# Wait a moment for the server to initialize
sleep 3

# Start the electron app
echo "Starting electron app..."
cd "$SCRIPT_DIR"
bun dev &
APP_PID=$!

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down ITO..."
    kill $APP_PID 2>/dev/null
    cd "$SCRIPT_DIR/server"
    docker compose down
    exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo ""
echo "ITO is running!"
echo "Press Ctrl+C to stop both server and app."
echo ""

# Wait for either process to exit
wait
