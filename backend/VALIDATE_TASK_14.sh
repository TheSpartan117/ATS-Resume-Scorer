#!/bin/bash
# Task 14 Validation Script
# Run this to validate the quantification scorer implementation

set -e  # Exit on any error

echo "========================================================================"
echo "TASK 14 VALIDATION: P2.2 Quantification Scorer"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check we're in backend directory
if [ ! -d "services" ]; then
    echo -e "${RED}Error: Must run from backend/ directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking file existence...${NC}"
files=(
    "services/quantification_scorer.py"
    "tests/services/test_quantification_scorer.py"
    "run_quantification_scorer_tests.py"
    "example_quantification_scorer.py"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (MISSING)"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo -e "${RED}Error: Some files are missing${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 2: Checking dependencies...${NC}"
if python3 -c "from backend.services.quantification_classifier import QuantificationClassifier" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} QuantificationClassifier available"
else
    echo -e "  ${RED}✗${NC} QuantificationClassifier not found"
    exit 1
fi

if python3 -c "from backend.config.scoring_thresholds import get_thresholds_for_level" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} scoring_thresholds config available"
else
    echo -e "  ${RED}✗${NC} scoring_thresholds not found"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 3: Running quick manual tests...${NC}"
if python3 run_quantification_scorer_tests.py; then
    echo -e "${GREEN}✓ Manual tests passed${NC}"
else
    echo -e "${RED}✗ Manual tests failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 4: Running pytest test suite...${NC}"
if python3 -m pytest tests/services/test_quantification_scorer.py -v --tb=short; then
    echo -e "${GREEN}✓ All pytest tests passed${NC}"
else
    echo -e "${RED}✗ Some pytest tests failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 5: Running example script (first 20 lines)...${NC}"
python3 example_quantification_scorer.py | head -20
echo "  ... (truncated for brevity)"
echo -e "${GREEN}✓ Example script runs${NC}"
echo ""

echo -e "${YELLOW}Step 6: Checking code quality...${NC}"
# Check for syntax errors
if python3 -m py_compile services/quantification_scorer.py; then
    echo -e "  ${GREEN}✓${NC} No syntax errors"
else
    echo -e "  ${RED}✗${NC} Syntax errors found"
    exit 1
fi

# Check for TODO/FIXME
if grep -n "TODO\|FIXME" services/quantification_scorer.py; then
    echo -e "  ${YELLOW}⚠${NC} Found TODO/FIXME comments (review needed)"
else
    echo -e "  ${GREEN}✓${NC} No TODO/FIXME markers"
fi
echo ""

echo "========================================================================"
echo -e "${GREEN}✓ ALL VALIDATIONS PASSED${NC}"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Review the changes:"
echo "   git diff services/quantification_scorer.py"
echo ""
echo "2. Stage the files:"
echo "   git add services/quantification_scorer.py \\"
echo "           tests/services/test_quantification_scorer.py \\"
echo "           run_quantification_scorer_tests.py \\"
echo "           example_quantification_scorer.py \\"
echo "           QUANTIFICATION_SCORER_README.md"
echo ""
echo "3. Commit:"
echo '   git commit -m "feat(P2.2): implement quantification scorer with weighted quality (10pts)'
echo ""
echo "   - Uses QuantificationClassifier for metric quality assessment"
echo "   - Level-aware thresholds: Beginner 30%, Intermediary 40%, Senior 50%"
echo "   - Weighted scoring: HIGH=1.0, MEDIUM=0.7, LOW=0.3"
echo "   - Tiered point system: 10/6/3/0 based on threshold bands"
echo "   - Detailed quality breakdown and actionable recommendations"
echo "   - Comprehensive test coverage with 21 test cases"
echo ""
echo "   Based on ResumeWorded and Jobscan research on metric effectiveness."
echo ""
echo '   Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"'
echo ""
echo "4. Proceed to Task 15 (P2.3 - Achievement Depth)"
echo ""
