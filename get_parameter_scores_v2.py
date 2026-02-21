#!/usr/bin/env python3
"""Get detailed parameter scores for all 3 CVs using ScorerV3 directly."""
import sys
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.parser import parse_pdf
from backend.services.scorer_v3 import ScorerV3
from backend.services.scorer_v3_adapter import ScorerV3Adapter

# Test CVs with ResumeWorded target scores
TEST_CVS = [
    {
        'name': 'Sabuj Mondal',
        'path': '/Users/sabuj.mondal/Downloads/Sabuj_Mondal_PM_CV.pdf',
        'role': 'product_manager',
        'level': 'senior',
        'target_score': 86
    },
    {
        'name': 'Aishik Das',
        'path': '/Users/sabuj.mondal/Downloads/AISHIK DAS_CV_v2.pdf',
        'role': 'product_manager',
        'level': 'mid',
        'target_score': 81
    },
    {
        'name': 'Swastik Paul',
        'path': '/Users/sabuj.mondal/Downloads/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2.pdf',
        'role': 'product_manager',
        'level': 'mid',
        'target_score': 65
    }
]

# Parameter registry (only scored parameters, not penalties/metadata)
PARAMS = [
    ("P1.1", "Required Keywords", 25),
    ("P1.2", "Preferred Keywords", 10),
    ("P2.1", "Action Verbs", 15),
    ("P2.2", "Quantification", 10),
    ("P2.3", "Achievement Depth", 5),
    ("P3.1", "Page Count", 5),
    ("P3.2", "Word Count", 3),
    ("P3.3", "Section Balance", 5),
    ("P3.4", "ATS Formatting", 7),
    ("P4.1", "Grammar", 10),
    ("P4.2", "Professional Standards", 5),
    ("P5.1", "Years Alignment", 10),
    ("P7.1", "Readability", 5),
    ("P7.2", "Bullet Structure", 3),
    ("P7.3", "Passive Voice", 2),
]

def score_cv(cv_info):
    """Score a CV and return result."""
    with open(cv_info['path'], 'rb') as f:
        resume_data = parse_pdf(f.read(), cv_info['name'] + '.pdf')

    # Use adapter to convert and score
    adapter = ScorerV3Adapter()
    scorer_input = adapter._convert_resume_data(resume_data)

    # Create scorer and score directly
    scorer = ScorerV3()
    result = scorer.score(
        resume_data=scorer_input,
        job_requirements=None,  # No JD - will use default keywords based on role
        experience_level=cv_info['level'],
        role=cv_info['role']
    )
    return result

# Score all CVs
print("Scoring CVs...")
results = {}
for cv_info in TEST_CVS:
    try:
        result = score_cv(cv_info)
        results[cv_info['name']] = result
        print(f"  ✓ {cv_info['name']}: {result['raw_score']:.1f}/100")
    except Exception as e:
        print(f"  ✗ {cv_info['name']}: {e}")
        import traceback
        traceback.print_exc()
        results[cv_info['name']] = None

print("\n" + "="*130)
print("PARAMETER-BY-PARAMETER SCORES")
print("="*130)

# Header
print(f"{'Parameter':<35} {'Max':<6} {'Sabuj Mondal':<20} {'Aishik Das':<20} {'Swastik Paul':<20}")
print("-"*130)

# Extract parameter scores from results
def get_param_score(result, param_code):
    """Extract a parameter score from the result."""
    if not result:
        return None

    # Get from parameter_scores
    param_scores = result.get('parameter_scores', {})
    if param_code in param_scores:
        param_result = param_scores[param_code]
        if param_result.get('status') == 'success':
            return param_result.get('score', 0)
        elif param_result.get('status') == 'error':
            return 0.0  # Errored parameters score 0

    return None

# Display each parameter
for code, name, max_score in PARAMS:
    row = f"{code} {name:<30} {max_score:<6}"

    for cv_info in TEST_CVS:
        result = results.get(cv_info['name'])
        if result:
            param_score = get_param_score(result, code)

            if param_score is not None:
                pct = (param_score / max_score * 100) if max_score > 0 else 0
                status = "✓" if pct >= 80 else "⚠" if pct >= 50 else "✗"
                row += f" {status} {param_score:4.1f}/{max_score:<2d} ({pct:4.0f}%)   "
            else:
                row += f" - N/A              "
        else:
            row += f" - ERROR            "

    print(row)

# Print totals
print("-"*130)
total_row = f"{'TOTAL':<35} {'100':<6}"
for cv_info in TEST_CVS:
    result = results.get(cv_info['name'])
    if result:
        total = result.get('raw_score', 0)
        target = cv_info['target_score']
        diff = total - target
        status = "✓" if abs(diff) <= 5 else "⚠" if abs(diff) <= 15 else "✗"
        total_row += f" {status} {total:4.0f}/100 (T:{target:<2d})  "
    else:
        total_row += f" - ERROR            "

print(total_row)
print("="*130)
