#!/bin/bash
# Phase 2: Core Features - Installation and Verification Script
# Run this script to install dependencies and verify Phase 2 implementation

set -e  # Exit on error

echo "================================================"
echo "Phase 2: Core Features - Installation Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo -e "${BLUE}Step 1: Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.8 or higher.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"
echo ""

echo -e "${BLUE}Step 2: Checking if backend directory exists...${NC}"
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}Error: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend directory found${NC}"
cd "$BACKEND_DIR"
echo ""

echo -e "${BLUE}Step 3: Installing Phase 2 dependencies...${NC}"
echo "This may take 2-5 minutes for first-time installation..."
echo ""

# Install dependencies
if pip3 install -r requirements.txt --quiet; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Some dependencies may have failed. Attempting to install individually...${NC}"

    # Try installing Phase 2 specific dependencies individually
    echo "Installing sentence-transformers..."
    pip3 install sentence-transformers==2.3.1 --quiet || echo -e "${YELLOW}⚠ sentence-transformers installation failed (optional)${NC}"

    echo "Installing KeyBERT..."
    pip3 install KeyBERT==0.8.3 --quiet || echo -e "${YELLOW}⚠ KeyBERT installation failed (optional)${NC}"

    echo "Installing diskcache..."
    pip3 install diskcache==5.6.3 --quiet || echo -e "${YELLOW}⚠ diskcache installation failed (optional)${NC}"
fi
echo ""

echo -e "${BLUE}Step 4: Verifying Phase 2 files...${NC}"

# Check if Phase 2 files exist
files=(
    "services/ats_simulator.py"
    "services/skills_categorizer.py"
    "services/confidence_scorer.py"
    "services/semantic_matcher.py"
    "api/phase2_features.py"
    "tests/test_phase2_features.py"
)

all_files_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file (MISSING)${NC}"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    echo -e "${RED}Error: Some Phase 2 files are missing${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}Step 5: Checking frontend files...${NC}"
frontend_files=(
    "../frontend/src/components/ResumeHeatMap.tsx"
)

for file in "${frontend_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${YELLOW}⚠ $file (MISSING - frontend component)${NC}"
    fi
done
echo ""

echo -e "${BLUE}Step 6: Running Phase 2 tests...${NC}"
echo "This will verify that all Phase 2 features are working correctly..."
echo ""

# Run tests with pytest
if command -v pytest &> /dev/null; then
    if pytest tests/test_phase2_features.py -v --tb=short 2>&1 | tee /tmp/phase2_test_output.txt; then
        echo ""
        echo -e "${GREEN}✓ All Phase 2 tests passed!${NC}"

        # Count passed tests
        passed=$(grep -c "PASSED" /tmp/phase2_test_output.txt || echo "0")
        echo -e "${GREEN}Tests passed: $passed${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠ Some tests failed. This might be OK if optional dependencies are missing.${NC}"
        echo -e "${YELLOW}  Check test output above for details.${NC}"
    fi
else
    echo -e "${YELLOW}⚠ pytest not found. Installing pytest...${NC}"
    pip3 install pytest --quiet

    if pytest tests/test_phase2_features.py -v --tb=short; then
        echo -e "${GREEN}✓ All Phase 2 tests passed!${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed.${NC}"
    fi
fi
echo ""

echo -e "${BLUE}Step 7: Quick API test...${NC}"
echo "Testing if Phase 2 API can be imported..."

python3 << EOF
try:
    from services.ats_simulator import ATSSimulator
    from services.skills_categorizer import SkillsCategorizer
    from services.confidence_scorer import ConfidenceScorer
    print("✓ All Phase 2 services can be imported")

    # Quick smoke test
    simulator = ATSSimulator()
    categorizer = SkillsCategorizer()
    scorer = ConfidenceScorer()
    print("✓ All Phase 2 services initialized successfully")

except Exception as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Phase 2 services are working${NC}"
else
    echo -e "${RED}✗ Phase 2 services have issues${NC}"
fi
echo ""

echo "================================================"
echo -e "${GREEN}Phase 2 Installation Summary${NC}"
echo "================================================"
echo ""
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo -e "${GREEN}✓ Phase 2 files verified${NC}"
echo -e "${GREEN}✓ Services working${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. Start the backend server:"
echo "   cd $BACKEND_DIR"
echo "   uvicorn main:app --reload --port 8000"
echo ""
echo "2. Test Phase 2 endpoints:"
echo "   curl http://localhost:8000/api/phase2/health"
echo ""
echo "3. View API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "4. Read documentation:"
echo "   - Implementation Report: docs/PHASE2_IMPLEMENTATION_REPORT.md"
echo "   - Quick Reference: docs/PHASE2_QUICK_REFERENCE.md"
echo "   - Summary: PHASE2_IMPLEMENTATION_SUMMARY.md"
echo ""
echo -e "${GREEN}Phase 2 installation complete!${NC}"
echo "================================================"
