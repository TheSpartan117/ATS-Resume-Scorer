#!/bin/bash
# Test runner for update-section endpoint tests

echo "=========================================="
echo "Running Update Section Endpoint Tests"
echo "=========================================="
echo ""

cd /Users/sabuj.mondal/ats-resume-scorer/backend

echo "Step 1: Installing dependencies..."
pip install beautifulsoup4==4.12.3 -q

echo ""
echo "Step 2: Running tests..."
python -m pytest tests/test_update_section.py -v --tb=short

echo ""
echo "=========================================="
echo "Test execution complete"
echo "=========================================="
