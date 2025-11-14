#!/bin/bash
# Launch the AI Augmented Generative Sequencer in a new terminal window

clear
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║         Launching AI Augmented Generative Sequencer for Roland T-8...         ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. Please install it first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the looper
python3 acid_looper_curses.py

