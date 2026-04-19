#!/bin/bash
# NEM Studios Invoice Generator — Quick Launch
# Double-click or run: ./start.sh
# Automatically installs dependencies on first run.

cd "$(dirname "$0")"

# Check & install dependencies
if ! python3 -c "import reportlab" 2>/dev/null; then
    echo "📦 Installing dependencies (first run only)..."
    pip3 install -r requirements.txt
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║   NEM Studios Invoice Generator              ║"
echo "║   Open in browser: http://localhost:5678     ║"
echo "║   Press Ctrl+C to stop                       ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

python3 server.py
