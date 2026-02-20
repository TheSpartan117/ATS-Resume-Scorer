"""
Benchmark Tracker - Tracks score distributions and competitive positioning.

This module provides:
- Score distribution tracking by role and level
- Percentile calculations
- Competitive positioning analysis
- Outlier detection
"""

import statistics
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime


class BenchmarkTracker:
    """
    Tracks and analyzes score distributions for competitive benchmarking.

    Components:
    - Score tracking by role/level
    - Percentile calculations
    - Competitive tier assignment
    - Statistical analysis
    """

    def __init__(self):
        """Initialize tracker with empty score storage."""
        # Structure: {(role, level): [{'score': float, 'timestamp': str, 'metadata': dict}]}
        self.scores = defaultdict(list)
        self.min_sample_size = 10  # Minimum scores needed for reliable statistics

    def track_score(
        self,
        score: float,
        role: str,
        level: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Track a resume score.

        Args:
            score: Overall quality score
            role: Role identifier (e.g., "software_engineer")
            level: Experience level (e.g., "senior")
            metadata: Optional additional data about the resume
        """
        key = (role, level)
        entry = {
            'score': score,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.scores[key].append(entry)

    def get_score_count(self, role: Optional[str] = None, level: Optional[str] = None) -> int:
        """
        Get count of tracked scores.

        Args:
            role: Optional role filter
            level: Optional level filter

        Returns:
            Count of scores matching filters
        """
        if role and level:
            return len(self.scores.get((role, level), []))
        elif role:
            return sum(len(scores) for (r, l), scores in self.scores.items() if r == role)
        elif level:
            return sum(len(scores) for (r, l), scores in self.scores.items() if l == level)
        else:
            return sum(len(scores) for scores in self.scores.values())

    def get_distribution(self, role: str, level: Optional[str] = None) -> Dict:
        """
        Get score distribution for a role/level.

        Args:
            role: Role identifier
            level: Optional level filter

        Returns:
            Dictionary with distribution statistics
        """
        if level:
            score_data = self.scores.get((role, level), [])
        else:
            # Aggregate all levels for this role
            score_data = []
            for (r, l), scores in self.scores.items():
                if r == role:
                    score_data.extend(scores)

        if not score_data:
            return {
                'count': 0,
                'mean': 0,
                'median': 0,
                'message': 'No data available'
            }

        scores = [entry['score'] for entry in score_data]

        return {
            'count': len(scores),
            'mean': statistics.mean(scores),
            'median': statistics.median(scores),
            'min': min(scores),
            'max': max(scores),
            'std_dev': statistics.stdev(scores) if len(scores) > 1 else 0
        }

    def calculate_percentile(
        self,
        score: float,
        role: str,
        level: str
    ) -> Optional[float]:
        """
        Calculate percentile rank for a score.

        Args:
            score: Score to rank
            role: Role identifier
            level: Experience level

        Returns:
            Percentile (0-100) or None if insufficient data
        """
        key = (role, level)
        score_data = self.scores.get(key, [])

        if len(score_data) < self.min_sample_size:
            return None  # Insufficient data

        scores = sorted([entry['score'] for entry in score_data])

        # Count scores below the given score
        count_below = sum(1 for s in scores if s < score)

        # Calculate percentile
        percentile = (count_below / len(scores)) * 100

        return round(percentile, 1)

    def get_competitive_position(
        self,
        score: float,
        role: str,
        level: str
    ) -> Dict:
        """
        Get competitive positioning for a score.

        Args:
            score: Resume score
            role: Role identifier
            level: Experience level

        Returns:
            Dictionary with tier, percentile, and positioning message
        """
        percentile = self.calculate_percentile(score, role, level)

        if percentile is None:
            return {
                'tier': 'unknown',
                'percentile': None,
                'message': 'Insufficient benchmark data for comparison',
                'sample_size': len(self.scores.get((role, level), []))
            }

        # Assign tier based on percentile
        if percentile >= 90:
            tier = 'top'
            message = 'Top 10% - Exceptional resume, highly competitive for elite positions'
        elif percentile >= 75:
            tier = 'competitive'
            message = 'Top 25% - Strong resume, competitive for most positions'
        elif percentile >= 50:
            tier = 'above_average'
            message = 'Above average - Solid resume with room for improvement'
        elif percentile >= 25:
            tier = 'below_average'
            message = 'Below average - Significant improvements recommended'
        else:
            tier = 'needs_improvement'
            message = 'Bottom 25% - Substantial work needed to be competitive'

        return {
            'tier': tier,
            'percentile': percentile,
            'message': message,
            'sample_size': len(self.scores.get((role, level), []))
        }

    def identify_outliers(
        self,
        role: str,
        level: str,
        threshold: float = 3.0
    ) -> List[Dict]:
        """
        Identify statistical outliers (scores beyond ±3 std dev).

        Args:
            role: Role identifier
            level: Experience level
            threshold: Standard deviation threshold (default: 3.0)

        Returns:
            List of outlier entries
        """
        key = (role, level)
        score_data = self.scores.get(key, [])

        if len(score_data) < self.min_sample_size:
            return []

        scores = [entry['score'] for entry in score_data]
        mean = statistics.mean(scores)
        std_dev = statistics.stdev(scores) if len(scores) > 1 else 0

        if std_dev == 0:
            return []

        outliers = []
        for entry in score_data:
            z_score = abs(entry['score'] - mean) / std_dev
            if z_score > threshold:
                outliers.append({
                    'score': entry['score'],
                    'z_score': round(z_score, 2),
                    'type': 'high' if entry['score'] > mean else 'low',
                    'timestamp': entry['timestamp']
                })

        return outliers

    def get_statistics(
        self,
        role: str,
        level: str
    ) -> Dict:
        """
        Get comprehensive statistics for a role/level.

        Args:
            role: Role identifier
            level: Experience level

        Returns:
            Dictionary with statistical measures
        """
        key = (role, level)
        score_data = self.scores.get(key, [])

        if not score_data:
            return {
                'count': 0,
                'message': 'No data available'
            }

        scores = [entry['score'] for entry in score_data]

        stats = {
            'count': len(scores),
            'mean': round(statistics.mean(scores), 2),
            'median': round(statistics.median(scores), 2),
            'min': min(scores),
            'max': max(scores),
        }

        if len(scores) > 1:
            stats['std_dev'] = round(statistics.stdev(scores), 2)
            stats['variance'] = round(statistics.variance(scores), 2)

        # Calculate quartiles
        if len(scores) >= 4:
            sorted_scores = sorted(scores)
            stats['q1'] = round(statistics.median(sorted_scores[:len(sorted_scores)//2]), 2)
            stats['q3'] = round(statistics.median(sorted_scores[(len(sorted_scores)+1)//2:]), 2)

        return stats

    def compare_to_benchmark(
        self,
        score: float,
        role: str,
        level: str
    ) -> Dict:
        """
        Compare a score to benchmark data.

        Args:
            score: Score to compare
            role: Role identifier
            level: Experience level

        Returns:
            Comprehensive comparison with percentile, tier, and insights
        """
        stats = self.get_statistics(role, level)

        if stats.get('count', 0) < self.min_sample_size:
            return {
                'percentile': None,
                'vs_average': 0,
                'tier': 'unknown',
                'message': f'Insufficient data (need {self.min_sample_size}, have {stats.get("count", 0)})',
                'statistics': stats
            }

        position = self.get_competitive_position(score, role, level)
        mean = stats['mean']

        # Calculate difference from average
        vs_average = round(score - mean, 1)
        vs_average_pct = round((vs_average / mean) * 100, 1) if mean > 0 else 0

        # Generate message
        if vs_average > 0:
            message = f"{vs_average} points above average (+{abs(vs_average_pct)}%)"
        elif vs_average < 0:
            message = f"{abs(vs_average)} points below average ({vs_average_pct}%)"
        else:
            message = "Exactly at average"

        return {
            'percentile': position['percentile'],
            'vs_average': vs_average,
            'vs_average_pct': vs_average_pct,
            'tier': position['tier'],
            'message': message,
            'positioning_message': position['message'],
            'statistics': stats
        }
