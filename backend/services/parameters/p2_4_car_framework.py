"""
P2.4 - CAR/STAR Framework Scoring (15 pts)

Evaluates bullet points based on Context-Action-Result (CAR) or STAR framework structure.

Research basis:
- ResumeWorded: CAR structure bullets score 2.5x higher than duty statements
- Jobscan: 87% of top-performing resumes use CAR framework extensively
- LinkedIn: CAR bullets get 3x more recruiter engagement
- Achievement statements > responsibility statements across all ATS platforms

Framework Components:
- Context (C): Sets the scene (team size, problem scope, business need)
- Action (A): Strong verb describing what YOU did (not team/company)
- Result (R): Quantified outcome with business impact
- Causality: Clear connection between action and result

Implementation:
- Perfect CAR (14-15 pts per bullet): All 4 components + multiple metrics
  Example: "Led migration of 20 microservices to Kubernetes (Context), reducing
  infrastructure costs by 45% ($200K/year) and deployment time from 2 hours to
  15 minutes (Result with causality)"

- Strong AR (12-13 pts per bullet): Action + Result with metrics
  Example: "Optimized database queries reducing page load time by 60% for 1M+ users"

- Moderate A (8-10 pts per bullet): Action + vague result
  Example: "Improved system performance through code optimization"

- Weak (3-4 pts per bullet): Duty statement only
  Example: "Responsible for database optimization"

Score calculation: Average CAR score across all bullets (max 15 pts)

Level-specific thresholds:
- Beginner: 50% bullets with AR structure = 10 pts
- Intermediary: 60% with AR, 30% with CAR = 12 pts
- Senior: 70% with AR, 50% with CAR = 15 pts

References:
- ResumeWorded CAR scoring methodology
- Jobscan achievement statement analysis
- LinkedIn recruiter engagement metrics
- Harvard Career Services resume guidelines
"""

from typing import Dict, List
from backend.services.content_impact_analyzer import ContentImpactAnalyzer


class CARFrameworkScorer:
    """
    Score resume bullets based on CAR/STAR framework structure.

    Leverages existing ContentImpactAnalyzer for sophisticated
    achievement structure detection.

    Scoring:
    - 15 points: Excellent CAR usage (70%+ bullets with strong structure)
    - 12 points: Good AR usage (60%+ bullets with action + result)
    - 9 points: Moderate (40-60% with results)
    - 6 points: Weak (20-40% with results)
    - 3 points: Poor (<20% with results)
    """

    def __init__(self):
        """Initialize CAR framework scorer"""
        self.max_points = 15
        self.analyzer = ContentImpactAnalyzer()

    def score(self, bullets: List[str], level: str = "intermediary") -> Dict:
        """
        Score bullets based on CAR/STAR framework usage.

        Args:
            bullets: List of experience bullet points
            level: Experience level (beginner, intermediary, senior)

        Returns:
            Dictionary with:
            - score: Points (0-15)
            - max_score: Maximum possible points (15)
            - percentage: Score as percentage
            - car_breakdown: Analysis of each bullet
            - summary: Overall CAR usage statistics
            - details: Human-readable feedback
        """
        if not bullets or len(bullets) == 0:
            return {
                'score': 0,
                'max_score': self.max_points,
                'percentage': 0,
                'car_breakdown': [],
                'summary': {
                    'total_bullets': 0,
                    'perfect_car': 0,
                    'strong_ar': 0,
                    'moderate': 0,
                    'weak': 0
                },
                'details': 'No bullet points found to analyze',
                'parameter': 'P2.4',
                'name': 'CAR/STAR Framework'
            }

        # Analyze each bullet for CAR structure
        car_breakdown = []
        category_counts = {
            'perfect_car': 0,      # 14-15 pts
            'strong_ar': 0,         # 12-13 pts
            'moderate': 0,          # 8-10 pts
            'weak': 0,              # 3-7 pts
            'very_weak': 0          # 0-2 pts
        }

        for bullet in bullets:
            # Skip empty or very short bullets
            if not bullet or len(bullet.strip()) < 10:
                continue

            # Analyze CAR structure using existing analyzer
            analysis = self.analyzer.analyze_achievement_structure(bullet)
            bullet_score = analysis['score']

            # Apply level-based adjustments
            adjusted_score = self.analyzer._adjust_score_for_level(
                bullet_score,
                level,
                bullet
            )

            # Categorize bullet
            if adjusted_score >= 14:
                category = 'perfect_car'
                category_counts['perfect_car'] += 1
            elif adjusted_score >= 12:
                category = 'strong_ar'
                category_counts['strong_ar'] += 1
            elif adjusted_score >= 8:
                category = 'moderate'
                category_counts['moderate'] += 1
            elif adjusted_score >= 3:
                category = 'weak'
                category_counts['weak'] += 1
            else:
                category = 'very_weak'
                category_counts['very_weak'] += 1

            car_breakdown.append({
                'bullet': bullet[:100] + '...' if len(bullet) > 100 else bullet,
                'score': adjusted_score,
                'category': category,
                'has_context': analysis['has_context'],
                'action_verb': analysis['action_verb'],
                'action_strength': analysis['action_strength'],
                'metrics_count': len(analysis['metrics_found']),
                'has_causality': analysis['has_causality'],
                'explanation': analysis['explanation']
            })

        # Calculate overall score using existing method
        # This gives us a score out of 15 already
        final_score = self.analyzer.score_achievement_strength(bullets, level)

        # Calculate statistics
        total_bullets = len(car_breakdown)
        perfect_car_pct = (category_counts['perfect_car'] / total_bullets * 100) if total_bullets > 0 else 0
        strong_ar_pct = (category_counts['strong_ar'] / total_bullets * 100) if total_bullets > 0 else 0
        good_bullets_pct = ((category_counts['perfect_car'] + category_counts['strong_ar']) / total_bullets * 100) if total_bullets > 0 else 0

        # Generate feedback based on level and performance
        feedback = self._generate_feedback(
            final_score,
            level,
            perfect_car_pct,
            strong_ar_pct,
            good_bullets_pct,
            total_bullets
        )

        return {
            'score': round(final_score, 1),
            'max_score': self.max_points,
            'percentage': round((final_score / self.max_points) * 100, 1),
            'car_breakdown': car_breakdown[:5],  # Show top 5 for space
            'summary': {
                'total_bullets': total_bullets,
                'perfect_car': category_counts['perfect_car'],
                'perfect_car_pct': round(perfect_car_pct, 1),
                'strong_ar': category_counts['strong_ar'],
                'strong_ar_pct': round(strong_ar_pct, 1),
                'good_bullets_pct': round(good_bullets_pct, 1),
                'moderate': category_counts['moderate'],
                'weak': category_counts['weak'],
                'very_weak': category_counts['very_weak']
            },
            'details': feedback,
            'parameter': 'P2.4',
            'name': 'CAR/STAR Framework'
        }

    def _generate_feedback(
        self,
        score: float,
        level: str,
        perfect_car_pct: float,
        strong_ar_pct: float,
        good_bullets_pct: float,
        total_bullets: int
    ) -> str:
        """Generate detailed feedback based on CAR usage"""

        # Level-specific thresholds
        thresholds = {
            'beginner': {'good': 50, 'excellent': 70},
            'intermediary': {'good': 60, 'excellent': 80},
            'senior': {'good': 70, 'excellent': 85}
        }

        level_thresholds = thresholds.get(level, thresholds['intermediary'])

        if good_bullets_pct >= level_thresholds['excellent']:
            feedback = f"Excellent CAR framework usage! {good_bullets_pct:.0f}% of bullets have strong Context-Action-Result structure with quantified outcomes. This significantly strengthens your resume."
        elif good_bullets_pct >= level_thresholds['good']:
            feedback = f"Good use of CAR framework ({good_bullets_pct:.0f}% of bullets). To reach excellence for {level} level, aim for {level_thresholds['excellent']}%+ bullets with full Context-Action-Result structure."
        elif good_bullets_pct >= 40:
            feedback = f"Moderate CAR usage ({good_bullets_pct:.0f}% of bullets). Many bullets lack clear results. Add metrics and outcomes: 'Reduced X by Y%', 'Increased Z to $W', 'Improved A by B minutes'."
        elif good_bullets_pct >= 20:
            feedback = f"Weak CAR structure ({good_bullets_pct:.0f}% of bullets). Most bullets are duty statements without results. Transform 'Responsible for X' into 'Led X initiative reducing costs by 30% ($200K/year)'."
        else:
            feedback = f"Very weak achievement structure. {total_bullets} bullets analyzed but only {good_bullets_pct:.0f}% have measurable outcomes. Focus on WHAT you accomplished, not just WHAT you did. Use Context-Action-Result format."

        # Add specific suggestions based on what's missing
        if perfect_car_pct < 20:
            feedback += " Add more context (team size, problem scope) to strengthen your achievements."
        if strong_ar_pct < 30:
            feedback += " Include more quantified results (%, $, time saved, users impacted)."

        return feedback


def create_scorer() -> CARFrameworkScorer:
    """
    Factory function to create CARFrameworkScorer instance.

    Returns:
        CARFrameworkScorer instance
    """
    return CARFrameworkScorer()
