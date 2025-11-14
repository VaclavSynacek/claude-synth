#!/bin/bash
# Launch the AI Augmented Generative Sequencer in a new terminal window
#
# Usage:
#   ./run_looper.sh [patches-directory]
#
# Examples:
#   ./run_looper.sh                    # Uses default 'patches' directory
#   ./run_looper.sh swing-patches      # Uses 'swing-patches' directory
#   ./run_looper.sh test-patches       # Uses 'test-patches' directory

# Get patches directory from argument, default to 'patches'
PATCHES_DIR="${1:-patches}"

clear
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                                ║"
echo "║         Launching AI Augmented Generative Sequencer for Roland T-8...         ║"
echo "║                                                                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Patches directory: ${PATCHES_DIR}"
echo ""

# Check if patches directory exists
if [ ! -d "${PATCHES_DIR}" ]; then
    echo "❌ Error: Directory '${PATCHES_DIR}' does not exist!"
    echo ""
    echo "Available patch directories:"
    ls -d */ 2>/dev/null | grep -E "(patches|test)" | sed 's|/$||' | sed 's/^/  - /'
    echo ""
    echo "Usage: $0 [patches-directory]"
    exit 1
fi

# Check if directory has any .json files
if ! ls "${PATCHES_DIR}"/*.json 1> /dev/null 2>&1; then
    echo "⚠️  Warning: No .json patch files found in '${PATCHES_DIR}'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' is not installed. Please install it first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the looper with the specified patches directory
python3 acid_looper_curses.py "${PATCHES_DIR}"

