"""
P2.5 - Impact Scope Indicators (10 pts)

Measures the scale and breadth of candidate's impact across different dimensions.

Research basis:
- Lever: Uses scope as multiplier for achievement weight (2x for org-wide impact)
- LinkedIn: Senior roles require evidence of "scale and impact"
- 68% of hiring managers cite "demonstrated scope" as top differentiator
- Greenhouse: Scope indicators increase match score by 15-20%

Scope Dimensions:
1. Team Size: Individual contributor vs leading teams vs org-level
   - 1-3 people: 2 pts (small team)
   - 4-9 people: 4 pts (medium team)
   - 10-19 people: 6 pts (large team)
   - 20-49 people: 8 pts (department)
   - 50+ people: 10 pts (organization-level)

2. Budget Responsibility: Project budgets vs department budgets
   - <$100K: 2 pts (small project)
   - $100K-$500K: 4 pts (medium project)
   - $500K-$5M: 7 pts (large project/department)
   - >$5M: 10 pts (major program)

3. User/Customer Scale: Reach and impact
   - <10K users: 2 pts (niche)
   - 10K-100K: 4 pts (substantial)
   - 100K-1M: 7 pts (large scale)
   - >1M: 10 pts (massive scale)

4. Geographic Scope: Local vs regional vs global
   - Single location: 2 pts
   - Regional: 4 pts
   - National: 6 pts
   - International/Global: 8-10 pts

Scoring: Take maximum scope across all dimensions (not cumulative)
Rationale: One dimension of massive scope is more impressive than multiple small scopes

Level-appropriate expectations:
- Beginner: IC scope (2-4 pts) acceptable
- Intermediary: Team/project scope (5-7 pts) expected
- Senior: Multi-team/org scope (8-10 pts) expected

References:
- Lever ATS scope weighting methodology
- LinkedIn senior role requirements
- Greenhouse impact scoring
- Top 10% resumes mention scope in 60%+ of bullets
"""

from typing import Dict, List
import re


class ImpactScopeScorer:
    """
    Score resume based on demonstrated impact scope across multiple dimensions.

    Evaluates:
    - Team size led/managed
    - Budget responsibility
    - User/customer scale
    - Geographic reach

    Takes maximum score across dimensions (one massive scope > multiple small scopes)
    """

    def __init__(self):
        """Initialize impact scope scorer with patterns"""
        self.max_points = 10

        # Team size patterns
        self.team_patterns = [
            r'(?:led|managed|supervised|directed|oversaw|mentored|coached)\s+(?:a\s+)?(?:team\s+of\s+)?(\d+)\s*(?:\+)?\s*(?:people|engineers|developers|designers|members|individuals|employees|reports)',
            r'(?:leading|managing|supervising)\s+(\d+)\s*(?:\+)?\s*(?:people|engineers|developers|designers|members)',
            r'(\d+)\s*(?:\+)?\s*(?:person|member)\s+team',
            r'team\s+of\s+(\d+)\s*(?:\+)?'
        ]

        # Budget patterns
        self.budget_patterns = [
            r'(?:budget|spend|investment|funding)\s+of\s+\$(\d+(?:\.\d+)?)\s*([KMB])',
            r'\$(\d+(?:\.\d+)?)\s*([KMB])\s+(?:budget|spend|investment|funding)',
            r'(?:managed|oversaw|responsible\s+for)\s+\$(\d+(?:\.\d+)?)\s*([KMB])',
            r'(\d+(?:\.\d+)?)\s*([KMB])\s+(?:dollar|USD)\s+(?:budget|project)'
        ]

        # User/customer scale patterns
        self.user_patterns = [
            r'(\d+(?:\.\d+)?)\s*([KMB])?\+?\s*(?:users|customers|clients|subscribers|members|employees)',
            r'(?:serving|impacting|supporting|reaching)\s+(\d+(?:\.\d+)?)\s*([KMB])?\+?\s*(?:users|customers|clients)',
            r'user\s+base\s+of\s+(\d+(?:\.\d+)?)\s*([KMB])?\+?',
            r'for\s+(\d+(?:\.\d+)?)\s*([KMB])?\+?\s*(?:users|customers)'
        ]

        # Geographic scope patterns
        self.geo_patterns = {
            'global': [
                r'\bglobal\b', r'\bworldwide\b', r'\binternational\b',
                r'\bmulti-country\b', r'\bcross-border\b', r'\bacross\s+\d+\s+countries'
            ],
            'national': [
                r'\bnationwide\b', r'\bacross\s+(?:the\s+)?(?:US|USA|country|nation)\b',
                r'\ball\s+states\b', r'\bnational\s+rollout\b'
            ],
            'regional': [
                r'\bregional\b', r'\bmulti-state\b', r'\bacross\s+\d+\s+(?:states|cities|offices)\b',
                r'\bEMEA\b', r'\bAPAC\b', r'\bAmericas\b'
            ],
            'local': [
                r'\bsite\b', r'\boffice\b', r'\blocal\b', r'\bsingle\s+location\b'
            ]
        }

        # Scoring thresholds
        self.team_thresholds = [
            (50, 10), (20, 8), (10, 6), (4, 4), (1, 2)
        ]

        self.budget_thresholds = [
            (5000, 10),    # $5M+
            (500, 7),      # $500K+
            (100, 4),      # $100K+
            (0, 2)         # Any budget
        ]

        self.user_thresholds = [
            (1000, 10),    # 1M+
            (100, 7),      # 100K+
            (10, 4),       # 10K+
            (0, 2)         # Any users
        ]

        self.geo_scores = {
            'global': 10,
            'national': 6,
            'regional': 4,
            'local': 2
        }

    def score(self, bullets: List[str]) -> Dict:
        """
        Score impact scope across all bullets.

        Args:
            bullets: List of experience bullet points

        Returns:
            Dictionary with:
            - score: Points (0-10)
            - max_score: Maximum possible points (10)
            - percentage: Score as percentage
            - team_scope: Best team size found
            - budget_scope: Best budget found
            - user_scope: Best user scale found
            - geo_scope: Best geographic scope found
            - details: Human-readable feedback
        """
        if not bullets or len(bullets) == 0:
            return {
                'score': 0,
                'max_score': self.max_points,
                'percentage': 0,
                'team_scope': None,
                'budget_scope': None,
                'user_scope': None,
                'geo_scope': None,
                'details': 'No bullet points found to analyze scope',
                'parameter': 'P2.5',
                'name': 'Impact Scope'
            }

        # Combine all bullets
        text = ' '.join(bullets).lower()

        # Extract scope across all dimensions
        team_size, team_score = self._extract_team_scope(text)
        budget_amount, budget_score = self._extract_budget_scope(text)
        user_count, user_score = self._extract_user_scope(text)
        geo_level, geo_score = self._extract_geo_scope(text)

        # Take maximum score (one massive scope > multiple small scopes)
        max_score = max(team_score, budget_score, user_score, geo_score)

        # Determine which dimension gave the max score
        max_dimension = self._identify_max_dimension(
            team_score, budget_score, user_score, geo_score
        )

        # Generate feedback
        feedback = self._generate_feedback(
            max_score,
            max_dimension,
            team_size,
            budget_amount,
            user_count,
            geo_level
        )

        return {
            'score': max_score,
            'max_score': self.max_points,
            'percentage': round((max_score / self.max_points) * 100, 1),
            'team_scope': team_size,
            'budget_scope': budget_amount,
            'user_scope': user_count,
            'geo_scope': geo_level,
            'max_dimension': max_dimension,
            'details': feedback,
            'parameter': 'P2.5',
            'name': 'Impact Scope'
        }

    def _extract_team_scope(self, text: str) -> tuple:
        """Extract team size mentions and score"""
        max_team = 0

        for pattern in self.team_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Handle both string and tuple matches
                    if isinstance(match, tuple):
                        team_size = int(match[0]) if match[0] else 0
                    else:
                        team_size = int(match)
                    max_team = max(max_team, team_size)
                except (ValueError, IndexError):
                    continue

        # Score based on thresholds
        team_score = 0
        for threshold, score in self.team_thresholds:
            if max_team >= threshold:
                team_score = score
                break

        return max_team if max_team > 0 else None, team_score

    def _extract_budget_scope(self, text: str) -> tuple:
        """Extract budget mentions and score"""
        max_budget = 0.0

        for pattern in self.budget_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if isinstance(match, tuple) and len(match) >= 2:
                        amount = float(match[0])
                        multiplier = match[1].upper()

                        # Convert to thousands
                        if multiplier == 'K':
                            amount_k = amount
                        elif multiplier == 'M':
                            amount_k = amount * 1000
                        elif multiplier == 'B':
                            amount_k = amount * 1000000
                        else:
                            amount_k = amount

                        max_budget = max(max_budget, amount_k)
                except (ValueError, IndexError):
                    continue

        # Score based on thresholds
        budget_score = 0
        for threshold, score in self.budget_thresholds:
            if max_budget >= threshold:
                budget_score = score
                break

        # Format budget for display
        if max_budget >= 1000:
            budget_display = f"${max_budget/1000:.1f}M"
        elif max_budget > 0:
            budget_display = f"${max_budget:.0f}K"
        else:
            budget_display = None

        return budget_display, budget_score

    def _extract_user_scope(self, text: str) -> tuple:
        """Extract user/customer scale and score"""
        max_users = 0.0

        for pattern in self.user_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        amount = float(match[0]) if match[0] else 0
                        multiplier = match[1].upper() if len(match) > 1 and match[1] else ''
                    else:
                        amount = float(match)
                        multiplier = ''

                    # Convert to thousands
                    if multiplier == 'K':
                        amount_k = amount
                    elif multiplier == 'M':
                        amount_k = amount * 1000
                    elif multiplier == 'B':
                        amount_k = amount * 1000000
                    else:
                        amount_k = amount / 1000  # Assume raw number is in units

                    max_users = max(max_users, amount_k)
                except (ValueError, IndexError):
                    continue

        # Score based on thresholds
        user_score = 0
        for threshold, score in self.user_thresholds:
            if max_users >= threshold:
                user_score = score
                break

        # Format for display
        if max_users >= 1000:
            user_display = f"{max_users/1000:.1f}M+"
        elif max_users > 0:
            user_display = f"{max_users:.0f}K+"
        else:
            user_display = None

        return user_display, user_score

    def _extract_geo_scope(self, text: str) -> tuple:
        """Extract geographic scope and score"""
        # Check in order of priority: global > national > regional > local
        for geo_level in ['global', 'national', 'regional', 'local']:
            for pattern in self.geo_patterns[geo_level]:
                if re.search(pattern, text, re.IGNORECASE):
                    return geo_level, self.geo_scores[geo_level]

        return None, 0

    def _identify_max_dimension(self, team: int, budget: int, users: int, geo: int) -> str:
        """Identify which dimension provided the maximum score"""
        scores = {
            'team_size': team,
            'budget': budget,
            'user_scale': users,
            'geographic': geo
        }

        max_dim = max(scores, key=scores.get)
        return max_dim if scores[max_dim] > 0 else None

    def _generate_feedback(
        self,
        score: int,
        max_dimension: str,
        team_size: int,
        budget: str,
        users: str,
        geo_level: str
    ) -> str:
        """Generate feedback based on scope findings"""

        if score == 0:
            return "No scope indicators found. Add scale metrics: team size managed, budget responsibility, users impacted, or geographic reach."

        # Build feedback based on what was found
        feedback_parts = []

        if score >= 8:
            feedback_parts.append(f"Excellent scope demonstrated ({score}/10 pts).")
        elif score >= 6:
            feedback_parts.append(f"Good scope indicators ({score}/10 pts).")
        elif score >= 4:
            feedback_parts.append(f"Moderate scope ({score}/10 pts).")
        else:
            feedback_parts.append(f"Limited scope shown ({score}/10 pts).")

        # Mention what was found
        found = []
        if team_size:
            found.append(f"managed {team_size} people")
        if budget:
            found.append(f"{budget} budget")
        if users:
            found.append(f"{users} users")
        if geo_level:
            found.append(f"{geo_level} reach")

        if found:
            feedback_parts.append("Found: " + ", ".join(found) + ".")

        # Suggestions for improvement
        if score < 8:
            suggestions = []
            if not team_size:
                suggestions.append("team size led")
            if not budget:
                suggestions.append("budget managed")
            if not users:
                suggestions.append("users impacted")
            if not geo_level:
                suggestions.append("geographic scope")

            if suggestions:
                feedback_parts.append(f"To improve, add: {', '.join(suggestions)}.")

        return " ".join(feedback_parts)


def create_scorer() -> ImpactScopeScorer:
    """
    Factory function to create ImpactScopeScorer instance.

    Returns:
        ImpactScopeScorer instance
    """
    return ImpactScopeScorer()
