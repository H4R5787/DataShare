#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "=========================================="
echo " Starting Secure Pass RxQ Application"
echo "=========================================="

if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    export PATH="/opt/homebrew/bin:$PATH"
    python3 -m venv backend/venv
    ./backend/venv/bin/pip install --upgrade pip
    ./backend/venv/bin/pip install -r backend/requirements.txt
fi

export PYTHONPATH="$DIR"
echo "Starting FastAPI server at http://127.0.0.1:8000"
echo "Interactive App: http://127.0.0.1:8000/"
echo "OpenAPI Specs:   http://127.0.0.1:8000/docs"
echo "=========================================="

./backend/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
