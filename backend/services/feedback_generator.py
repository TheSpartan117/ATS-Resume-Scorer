"""
Feedback Generator - Creates actionable, prioritized improvement suggestions.

This module provides:
- Actionable feedback generation
- Priority-based recommendations
- Score interpretation
- Complete feedback reports
"""

from typing import Dict, List


class FeedbackGenerator:
    """
    Generates actionable feedback and recommendations based on quality analysis.

    Components:
    - Achievement feedback
    - Clarity feedback
    - Specificity feedback
    - Priority assignment
    - Score interpretation
    """

    def generate_achievement_feedback(self, analysis: Dict) -> List[Dict]:
        """
        Generate achievement-specific feedback.

        Args:
            analysis: Dictionary with achievement scores and metrics

        Returns:
            List of feedback items with suggestions, priority, and examples
        """
        feedback = []
        achievement_score = analysis.get('achievement_strength', 0)
        metrics_found = analysis.get('metrics_found', 0)
        weak_verbs = analysis.get('weak_verbs_count', 0)

        # Critical: Very low achievement score
        if achievement_score < 5:
            feedback.append({
                'category': 'achievement',
                'priority': 'high',
                'suggestion': 'Add quantifiable results to demonstrate impact',
                'example': 'Instead of "Improved system performance", write "Optimized API reducing latency by 60% from 500ms to 200ms"',
                'impact': '+5-8 points'
            })

        # High priority: Missing metrics
        if metrics_found < 2:
            feedback.append({
                'category': 'achievement',
                'priority': 'high',
                'suggestion': 'Include specific numbers, percentages, or dollar amounts',
                'example': 'Add metrics like "Reduced costs by $2M" or "Increased conversion rate by 35%"',
                'impact': '+3-5 points'
            })

        # Medium priority: Weak action verbs
        if weak_verbs > 2:
            feedback.append({
                'category': 'achievement',
                'priority': 'medium',
                'suggestion': 'Replace weak verbs with strong action verbs',
                'example': 'Change "Responsible for managing" to "Led", "Helped with" to "Delivered", "Worked on" to "Architected"',
                'impact': '+2-4 points'
            })

        # Low priority: Good but could be better
        if 10 <= achievement_score < 12:
            feedback.append({
                'category': 'achievement',
                'priority': 'low',
                'suggestion': 'Add Context-Action-Result structure to more bullets',
                'example': 'Context: "In Q3 launch", Action: "Led team of 8", Result: "Delivered 3 features generating $2M ARR"',
                'impact': '+1-2 points'
            })

        return feedback

    def generate_clarity_feedback(self, analysis: Dict) -> List[Dict]:
        """
        Generate clarity-specific feedback.

        Args:
            analysis: Dictionary with clarity scores and metrics

        Returns:
            List of feedback items
        """
        feedback = []
        clarity_score = analysis.get('sentence_clarity', 0)
        weak_phrases = analysis.get('weak_phrases_found', [])
        passive_voice_pct = analysis.get('passive_voice_pct', 0)

        # High priority: Many weak phrases
        if len(weak_phrases) > 2:
            feedback.append({
                'category': 'clarity',
                'priority': 'high',
                'suggestion': f'Remove weak phrases: {", ".join(weak_phrases[:3])}',
                'example': 'Remove "responsible for", "worked on", "helped with" - start with strong verbs instead',
                'impact': '+3-4 points'
            })

        # Medium priority: Passive voice
        if passive_voice_pct > 40:
            feedback.append({
                'category': 'clarity',
                'priority': 'medium',
                'suggestion': 'Convert passive voice to active voice',
                'example': 'Change "Project was delivered by me" to "Delivered project"',
                'impact': '+2-3 points'
            })

        # Low priority: Sentence length
        if clarity_score < 8:
            feedback.append({
                'category': 'clarity',
                'priority': 'low',
                'suggestion': 'Adjust sentence length for optimal readability',
                'example': 'Aim for 15-25 words per bullet in experience section',
                'impact': '+1-2 points'
            })

        return feedback

    def generate_specificity_feedback(self, analysis: Dict) -> List[Dict]:
        """
        Generate specificity-specific feedback.

        Args:
            analysis: Dictionary with specificity scores

        Returns:
            List of feedback items
        """
        feedback = []
        specificity_score = analysis.get('specificity', 0)
        generic_tech = analysis.get('generic_tech_count', 0)
        vague_metrics = analysis.get('vague_metrics_count', 0)

        # High priority: Very low specificity
        if specificity_score < 2:
            feedback.append({
                'category': 'specificity',
                'priority': 'high',
                'suggestion': 'Replace generic terms with specific technologies and tools',
                'example': 'Change "databases" to "PostgreSQL and Redis", "frameworks" to "React and Node.js"',
                'impact': '+2-3 points'
            })

        # Medium priority: Vague metrics
        if vague_metrics > 1:
            feedback.append({
                'category': 'specificity',
                'priority': 'medium',
                'suggestion': 'Replace vague claims with precise numbers',
                'example': 'Change "significantly improved" to "improved by 45%", "many users" to "10,000+ users"',
                'impact': '+1-2 points'
            })

        # Low priority: Add more specific action verbs
        if specificity_score < 4:
            feedback.append({
                'category': 'specificity',
                'priority': 'low',
                'suggestion': 'Use more specific action verbs',
                'example': 'Replace "built" with "architected", "improved" with "optimized", "developed" with "engineered"',
                'impact': '+1 point'
            })

        return feedback

    def interpret_overall_score(self, score: float, level: str) -> Dict:
        """
        Interpret overall score with context.

        Args:
            score: Overall quality score (0-100)
            level: Experience level

        Returns:
            Dictionary with rating, message, and recommendations
        """
        level_context = {
            'entry': 'for entry-level position',
            'mid': 'for mid-level position',
            'senior': 'for senior position',
            'lead': 'for lead/principal position',
            'executive': 'for executive position'
        }

        context = level_context.get(level, 'for your experience level')

        if score >= 85:
            return {
                'rating': 'excellent',
                'message': f'Outstanding resume {context}. Highly competitive for top roles.',
                'next_steps': [
                    'Ready for applications to competitive positions',
                    'Consider minor polish for perfection',
                    'Tailor for specific companies/roles'
                ]
            }
        elif score >= 75:
            return {
                'rating': 'good',
                'message': f'Strong resume {context}. Competitive for most positions.',
                'improvements': [
                    'Focus on high-priority suggestions for maximum impact',
                    'Add more quantifiable achievements',
                    'Enhance specificity of technical details'
                ]
            }
        elif score >= 65:
            return {
                'rating': 'fair',
                'message': f'Decent resume {context}, but significant improvements needed.',
                'focus_areas': [
                    'Address all high-priority issues first',
                    'Add measurable impact to achievements',
                    'Improve clarity and remove weak phrases'
                ]
            }
        else:
            return {
                'rating': 'needs_improvement',
                'message': f'Resume needs substantial work {context}.',
                'focus_areas': [
                    'Start with achievement quantification',
                    'Remove all weak phrases and passive voice',
                    'Add specific technologies and metrics',
                    'Follow Context-Action-Result structure'
                ]
            }

    def generate_complete_feedback(
        self,
        analysis: Dict,
        level: str,
        section: str = "experience"
    ) -> Dict:
        """
        Generate complete feedback report.

        Args:
            analysis: Complete analysis results
            level: Experience level
            section: Resume section

        Returns:
            Complete feedback report with interpretation, suggestions, and priorities
        """
        overall_score = analysis.get('overall_score', 0)

        # Generate interpretation
        interpretation = self.interpret_overall_score(overall_score, level)

        # Generate all feedback
        all_suggestions = []
        all_suggestions.extend(self.generate_achievement_feedback(analysis))
        all_suggestions.extend(self.generate_clarity_feedback(analysis))
        all_suggestions.extend(self.generate_specificity_feedback(analysis))

        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_suggestions.sort(key=lambda x: priority_order.get(x['priority'], 3))

        # Extract priority actions (high priority only)
        priority_actions = [s for s in all_suggestions if s['priority'] == 'high']

        # Identify strengths
        strengths = []
        if analysis.get('achievement_strength', 0) >= 12:
            strengths.append('Strong quantifiable achievements')
        if analysis.get('sentence_clarity', 0) >= 8:
            strengths.append('Clear and concise writing')
        if analysis.get('specificity', 0) >= 4:
            strengths.append('Specific technical details')
        if analysis.get('grammar', 0) >= 9:
            strengths.append('Error-free presentation')

        return {
            'interpretation': interpretation,
            'suggestions': all_suggestions,
            'priority_actions': priority_actions,
            'strengths': strengths,
            'section': section,
            'level': level
        }
