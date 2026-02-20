"""
Quality Coach Scoring Calibration Script

This script tests the recalibrated Quality Coach scorer against known CV benchmarks
and provides tuning recommendations to achieve ±3 point accuracy with ResumeWorded.

Usage:
    python3 calibrate_quality_scorer.py --mode initial  # Test 3 known CVs
    python3 calibrate_quality_scorer.py --mode full     # Test 30 CVs
    python3 calibrate_quality_scorer.py --cv path/to/cv.docx --expected 86

Expected Scores (ResumeWorded baseline):
    - Sabuj CV: 86 points
    - Aishik CV: 80 points
    - Swastik CV: 65 points

Target Accuracy:
    - ±3 points on 90% of CVs
    - ±5 points on 100% of CVs
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.parser import parse_docx
from backend.services.scorer_quality import QualityScorer


# Known CV benchmarks (ResumeWorded scores)
KNOWN_CVS = {
    "sabuj": {
        "name": "Sabuj Mondal",
        "path": "backend/data/Sabuj_Mondal_PM_CV_1771577761468.docx",
        "expected_score": 86,
        "role": "product_manager",
        "level": "senior",
        "notes": "Strong achievement structure, specific metrics, excellent clarity"
    },
    "aishik": {
        "name": "Aishik (To be located)",
        "path": None,  # TO BE FOUND
        "expected_score": 80,
        "role": "product_manager",
        "level": "mid",
        "notes": "Good content but overly formatted - should NOT score higher than Sabuj"
    },
    "swastik": {
        "name": "Swastik Paul",
        "path": "backend/data/SWASTIK PAUL_CV_DIG_TRSFN STGY_PM-2_1771570503119.docx",
        "expected_score": 65,
        "role": "product_manager",
        "level": "mid",
        "notes": "Weak duty statements, lacks metrics, should score significantly lower"
    }
}


class CalibrationTester:
    """Tests and calibrates the Quality Coach scorer"""

    def __init__(self):
        self.scorer = QualityScorer()
        self.results = []

    def test_cv(
        self,
        cv_path: str,
        expected_score: int,
        role: str,
        level: str,
        cv_name: str = None
    ) -> Dict:
        """
        Test a single CV and compare against expected score.

        Args:
            cv_path: Path to CV file
            expected_score: Expected score from ResumeWorded
            role: Role identifier
            level: Experience level
            cv_name: Human-readable CV name

        Returns:
            Dictionary with test results
        """
        print(f"\n{'='*80}")
        print(f"Testing: {cv_name or cv_path}")
        print(f"Expected Score: {expected_score}")
        print(f"{'='*80}")

        # Parse CV
        try:
            resume_data = parse_docx(cv_path)
            if not resume_data:
                return {
                    "status": "error",
                    "error": "Failed to parse CV",
                    "cv_name": cv_name,
                    "cv_path": cv_path
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "cv_name": cv_name,
                "cv_path": cv_path
            }

        # Score CV
        try:
            score_result = self.scorer.score(
                resume_data=resume_data,
                role_id=role,
                level=level,
                job_description=None
            )
        except Exception as e:
            return {
                "status": "error",
                "error": f"Scoring failed: {str(e)}",
                "cv_name": cv_name,
                "cv_path": cv_path
            }

        # Calculate accuracy
        actual_score = score_result['score']
        delta = actual_score - expected_score
        abs_delta = abs(delta)
        accuracy_status = self._classify_accuracy(abs_delta)

        result = {
            "status": "success",
            "cv_name": cv_name,
            "cv_path": cv_path,
            "expected_score": expected_score,
            "actual_score": actual_score,
            "delta": delta,
            "abs_delta": abs_delta,
            "accuracy_status": accuracy_status,
            "breakdown": score_result.get('breakdown', {}),
            "timestamp": datetime.now().isoformat()
        }

        # Print results
        self._print_result(result)

        return result

    def _classify_accuracy(self, abs_delta: float) -> str:
        """Classify accuracy based on absolute delta"""
        if abs_delta <= 3:
            return "EXCELLENT (±3)"
        elif abs_delta <= 5:
            return "GOOD (±5)"
        elif abs_delta <= 8:
            return "ACCEPTABLE (±8)"
        else:
            return "NEEDS TUNING (>8)"

    def _print_result(self, result: Dict):
        """Print formatted test result"""
        if result["status"] == "error":
            print(f"\n❌ ERROR: {result['error']}")
            return

        expected = result['expected_score']
        actual = result['actual_score']
        delta = result['delta']
        status = result['accuracy_status']

        # Color-code output based on accuracy
        if "EXCELLENT" in status:
            icon = "✅"
        elif "GOOD" in status:
            icon = "✓"
        elif "ACCEPTABLE" in status:
            icon = "⚠️"
        else:
            icon = "❌"

        print(f"\n{icon} Actual Score: {actual}/100")
        print(f"   Delta: {delta:+.1f} points ({status})")

        # Print breakdown
        breakdown = result.get('breakdown', {})
        if breakdown:
            print(f"\nScore Breakdown:")
            for category, data in breakdown.items():
                if isinstance(data, dict) and 'score' in data:
                    print(f"  - {category}: {data['score']}/{data.get('max_score', '?')} pts")

    def test_known_cvs(self) -> List[Dict]:
        """Test all 3 known CVs"""
        results = []

        for cv_id, cv_data in KNOWN_CVS.items():
            if cv_data['path'] is None:
                print(f"\n⚠️  Skipping {cv_data['name']} - CV file not located")
                continue

            cv_path = Path(__file__).parent.parent / cv_data['path']
            if not cv_path.exists():
                print(f"\n⚠️  Skipping {cv_data['name']} - File not found: {cv_path}")
                continue

            result = self.test_cv(
                cv_path=str(cv_path),
                expected_score=cv_data['expected_score'],
                role=cv_data['role'],
                level=cv_data['level'],
                cv_name=cv_data['name']
            )
            results.append(result)

        self.results = results
        return results

    def print_summary(self, results: List[Dict]):
        """Print summary of all tests"""
        print(f"\n{'='*80}")
        print("CALIBRATION SUMMARY")
        print(f"{'='*80}")

        successful = [r for r in results if r['status'] == 'success']
        if not successful:
            print("❌ No successful tests")
            return

        # Calculate statistics
        deltas = [abs(r['abs_delta']) for r in successful]
        avg_delta = sum(deltas) / len(deltas)
        max_delta = max(deltas)
        within_3 = sum(1 for d in deltas if d <= 3)
        within_5 = sum(1 for d in deltas if d <= 5)

        total = len(successful)
        pct_within_3 = (within_3 / total) * 100
        pct_within_5 = (within_5 / total) * 100

        print(f"\nTested: {total} CVs")
        print(f"Average Delta: {avg_delta:.1f} points")
        print(f"Max Delta: {max_delta:.1f} points")
        print(f"Within ±3 points: {within_3}/{total} ({pct_within_3:.0f}%)")
        print(f"Within ±5 points: {within_5}/{total} ({pct_within_5:.0f}%)")

        # Target assessment
        print(f"\n{'='*80}")
        if pct_within_3 >= 90:
            print("✅ TARGET MET: ≥90% within ±3 points")
        elif pct_within_5 >= 90:
            print("⚠️  CLOSE: Need to tighten calibration to reach ±3 target")
        else:
            print("❌ NEEDS WORK: Significant calibration required")

        # Recommendations
        self._print_recommendations(results)

    def _print_recommendations(self, results: List[Dict]):
        """Print tuning recommendations based on results"""
        print(f"\n{'='*80}")
        print("TUNING RECOMMENDATIONS")
        print(f"{'='*80}")

        successful = [r for r in results if r['status'] == 'success']
        if not successful:
            return

        # Analyze score patterns
        over_scored = [r for r in successful if r['delta'] > 3]
        under_scored = [r for r in successful if r['delta'] < -3]

        if over_scored:
            print(f"\n⚠️  {len(over_scored)} CVs scored TOO HIGH:")
            for r in over_scored:
                print(f"   - {r['cv_name']}: {r['delta']:+.1f} points")
            print(f"\n   Recommendation:")
            print(f"   - Increase penalties for weak achievements")
            print(f"   - Strengthen CAR structure requirements")
            print(f"   - Add penalties for vague metrics")

        if under_scored:
            print(f"\n⚠️  {len(under_scored)} CVs scored TOO LOW:")
            for r in under_scored:
                print(f"   - {r['cv_name']}: {r['delta']:+.1f} points")
            print(f"\n   Recommendation:")
            print(f"   - Reduce penalties for minor issues")
            print(f"   - Give more credit for strong verb usage")
            print(f"   - Increase weight for quality metrics")

    def save_results(self, output_path: str = None):
        """Save calibration results to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"calibration_results_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results,
                "summary": {
                    "total_tested": len(self.results),
                    "successful": len([r for r in self.results if r['status'] == 'success']),
                    "failed": len([r for r in self.results if r['status'] == 'error'])
                }
            }, f, indent=2)

        print(f"\n📝 Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Calibrate Quality Coach scorer")
    parser.add_argument(
        '--mode',
        choices=['initial', 'full', 'single'],
        default='initial',
        help='Test mode: initial (3 CVs), full (30 CVs), or single CV'
    )
    parser.add_argument('--cv', help='Path to single CV (for single mode)')
    parser.add_argument('--expected', type=int, help='Expected score (for single mode)')
    parser.add_argument('--role', default='product_manager', help='Role ID')
    parser.add_argument('--level', default='mid', help='Experience level')
    parser.add_argument('--output', help='Output JSON file path')

    args = parser.parse_args()

    tester = CalibrationTester()

    if args.mode == 'single':
        if not args.cv or not args.expected:
            print("❌ Error: --cv and --expected required for single mode")
            sys.exit(1)

        result = tester.test_cv(
            cv_path=args.cv,
            expected_score=args.expected,
            role=args.role,
            level=args.level
        )
        tester.results = [result]

    elif args.mode == 'initial':
        print("\n🧪 TASK 16: Testing 3 Known CVs (Initial Calibration)")
        print("="*80)
        tester.test_known_cvs()

    elif args.mode == 'full':
        print("\n🧪 TASK 17: Testing 30 CVs (Full Calibration)")
        print("="*80)
        print("⚠️  Full calibration not yet implemented")
        print("   Need to expand test corpus to 30 CVs first")
        sys.exit(1)

    # Print summary
    tester.print_summary(tester.results)

    # Save results
    if args.output:
        tester.save_results(args.output)


if __name__ == "__main__":
    main()
