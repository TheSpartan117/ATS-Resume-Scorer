"""
Test script to verify scoring system is working correctly after fixes
Tests:
1. Scores don't exceed registry maximums
2. Category totals are correct
3. Overall total equals 100
"""
import sys
import os
sys.path.insert(0, '/Users/sabuj.mondal/ats-resume-scorer')

from backend.services.scorer_v3 import ScorerV3
from backend.services.parameters.registry import get_parameter_registry
from backend.services.parser import parse_pdf

def test_scoring_system():
    print("=" * 80)
    print("SCORING SYSTEM VERIFICATION TEST")
    print("=" * 80)

    registry = get_parameter_registry()
    all_scorers = registry.get_all_scorers()

    # Test 1: Verify registry totals 100
    print("\n1. Verifying Parameter Registry Totals...")
    category_totals = registry.get_max_score_by_category()
    total_max = registry.get_max_score()

    print(f"\nCategory Maximums:")
    for category, max_val in category_totals.items():
        print(f"  {category}: {max_val} pts")

    print(f"\nTotal Maximum: {total_max} pts")

    if total_max == 100:
        print("✅ Registry totals exactly 100 pts")
    else:
        print(f"❌ Registry totals {total_max} pts, expected 100")
        return False

    # Test 2: Test with a sample resume
    print("\n2. Testing with sample resume...")
    sample_pdf = "/Users/sabuj.mondal/ats-resume-scorer/backend/storage/uploads/0285f4ff-d559-4db1-8cbe-1745013509ae.pdf"

    try:
        with open(sample_pdf, 'rb') as f:
            pdf_content = f.read()

        resume_data = parse_pdf(pdf_content, "sample.pdf")
        print(f"✅ Parsed resume: {resume_data.metadata.get('wordCount', 0)} words")

        # Score the resume
        scorer = ScorerV3()
        result = scorer.score(resume_data=resume_data, experience_level='intermediary')

        print(f"\nOverall Score: {result['total_score']}/100")

        # Test 3: Verify no parameter exceeds its maximum
        print("\n3. Verifying parameter scores don't exceed maximums...")
        all_valid = True

        for category, details in result['category_scores'].items():
            print(f"\n  {category}: {details['score']:.1f}/{details['max']} pts")

            # Check each parameter in this category
            for param_code, param_result in details.get('parameters', {}).items():
                param_score = param_result['score']
                param_config = registry.get_scorer(param_code)
                param_max = param_config['max_score'] if param_config else 0

                if param_score > param_max:
                    print(f"    ❌ {param_code}: {param_score:.1f}/{param_max} pts - EXCEEDS MAXIMUM!")
                    all_valid = False
                else:
                    status = "✅" if param_score >= param_max * 0.7 else "⚠️" if param_score >= param_max * 0.4 else "❌"
                    print(f"    {status} {param_code}: {param_score:.1f}/{param_max} pts ({param_result['percentage']:.0f}%)")

        if all_valid:
            print("\n✅ All parameter scores are within their maximums")
        else:
            print("\n❌ Some parameter scores exceed their maximums!")
            return False

        # Test 4: Verify category totals match
        print("\n4. Verifying category score totals...")
        for category, details in result['category_scores'].items():
            category_score = details['score']
            category_max = details['max']

            # Sum up individual parameter scores
            param_sum = sum(p['score'] for p in details.get('parameters', {}).values())

            if abs(category_score - param_sum) > 0.01:  # Allow tiny floating point difference
                print(f"  ❌ {category}: Category score {category_score:.1f} != sum of parameters {param_sum:.1f}")
                all_valid = False
            else:
                print(f"  ✅ {category}: {category_score:.1f}/{category_max} pts (matches parameter sum)")

        # Test 5: Verify overall total
        print("\n5. Verifying overall total...")
        overall_from_categories = sum(d['score'] for d in result['category_scores'].values())

        if abs(result['total_score'] - overall_from_categories) > 0.01:
            print(f"  ❌ Overall score {result['total_score']:.1f} != sum of categories {overall_from_categories:.1f}")
            return False
        else:
            print(f"  ✅ Overall score {result['total_score']:.1f} matches sum of categories")

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED - Scoring system is working correctly!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_scoring_system()
    sys.exit(0 if success else 1)
