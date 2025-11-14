#!/bin/bash
# Test runner script for AI Augmented Generative Sequencer for Roland T-8
# This script runs the full test suite with coverage reporting

set -e  # Exit on error

echo "=========================================="
echo "AI Augmented Generative Sequencer for Roland T-8 - Test Suite"
echo "=========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed"
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Step 1: Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment..."
    uv venv
else
    echo "Virtual environment already exists"
fi

echo ""
echo "Step 2: Installing dependencies..."
source .venv/bin/activate
uv pip install -e ".[dev]"

echo ""
echo "Step 3: Running tests..."
echo "----------------------------------------"

# Run tests with different verbosity levels based on argument
if [ "$1" == "quick" ]; then
    echo "Running quick tests (no coverage)..."
    pytest -v
elif [ "$1" == "verbose" ]; then
    echo "Running verbose tests with coverage..."
    pytest -vv --cov=. --cov-report=term-missing --cov-report=html
elif [ "$1" == "unit" ]; then
    echo "Running unit tests only..."
    pytest tests/unit/ -v
elif [ "$1" == "integration" ]; then
    echo "Running integration tests only..."
    pytest tests/integration/ -v
else
    echo "Running all tests with coverage..."
    pytest -v --cov=. --cov-report=term-missing --cov-report=html
fi

echo ""
echo "=========================================="
echo "Test run complete!"
echo "=========================================="
echo ""

if [ "$1" != "quick" ] && [ "$1" != "unit" ] && [ "$1" != "integration" ]; then
    echo "Coverage report generated in: htmlcov/index.html"
    echo "Open with: xdg-open htmlcov/index.html"
    echo ""
fi

echo "Usage: ./run_tests.sh [quick|verbose|unit|integration]"
echo "  quick       - Fast test run without coverage"
echo "  verbose     - Detailed output with coverage"
echo "  unit        - Run unit tests only"
echo "  integration - Run integration tests only"
echo "  (default)   - Standard run with coverage"
