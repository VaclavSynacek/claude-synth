#!/bin/bash
# Launch the acid looper in a new terminal window

cd /home/jajis/projects/claude-synth

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                    Launching Acid Looper (Curses Edition)...                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "[INFO] Activating virtual environment..."

source .venv/bin/activate

echo "[INFO] Starting acid_looper_curses.py..."
echo ""

python3 acid_looper_curses.py
