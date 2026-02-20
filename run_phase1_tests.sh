#!/bin/bash
# Phase 1 Test Runner
# Run this script to validate Phase 1 implementation

echo "=========================================="
echo "Phase 1 Implementation Test Runner"
echo "=========================================="
echo ""

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

echo "Installing dependencies (if needed)..."
pip install -q pytest 2>/dev/null || echo "pytest already installed"

echo ""
echo "Running Phase 1 tests..."
echo ""

# Run tests with verbose output
python -m pytest tests/test_phase1_improvements.py -v -s

echo ""
echo "=========================================="
echo "Test run complete!"
echo "=========================================="
