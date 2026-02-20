"""
Phase 2 Features API Endpoints

Provides endpoints for:
- ATS Platform Simulation
- Hard/Soft Skills Categorization
- Keyword Heat Map Data
- Confidence Intervals
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from backend.services.ats_simulator import ATSSimulator, analyze_ats_compatibility
from backend.services.skills_categorizer import SkillsCategorizer, analyze_skills
from backend.services.confidence_scorer import ConfidenceScorer, add_confidence_intervals
from backend.services.semantic_matcher import SemanticKeywordMatcher


router = APIRouter(prefix="/api/phase2", tags=["phase2"])


# Request/Response Models

class ATSSimulationRequest(BaseModel):
    """Request for ATS platform simulation"""
    resume_text: str
    resume_metadata: Optional[Dict] = Field(default_factory=dict)


class SkillsAnalysisRequest(BaseModel):
    """Request for skills categorization"""
    resume_text: str
    job_description: Optional[str] = None


class HeatMapRequest(BaseModel):
    """Request for keyword heat map data"""
    resume_text: str
    job_description: str
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class ConfidenceRequest(BaseModel):
    """Request for confidence intervals"""
    scores: Dict[str, float]
    sample_sizes: Optional[Dict[str, int]] = None


# Endpoints

@router.post("/ats-simulation")
async def simulate_ats_platforms(request: ATSSimulationRequest) -> Dict[str, Any]:
    """
    Simulate how different ATS platforms will parse the resume.

    Returns compatibility scores for:
    - Taleo (strictest)
    - Workday (moderate)
    - Greenhouse (most lenient)

    Plus overall ATS compatibility score.
    """
    try:
        result = analyze_ats_compatibility(
            request.resume_text,
            request.resume_metadata
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ATS simulation failed: {str(e)}"
        )


@router.post("/ats-simulation/platform/{platform}")
async def simulate_specific_platform(
    platform: str,
    request: ATSSimulationRequest
) -> Dict[str, Any]:
    """
    Simulate a specific ATS platform.

    Supported platforms: taleo, workday, greenhouse
    """
    platform_lower = platform.lower()

    if platform_lower not in ['taleo', 'workday', 'greenhouse']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {platform}. Must be one of: taleo, workday, greenhouse"
        )

    try:
        simulator = ATSSimulator()

        if platform_lower == 'taleo':
            result = simulator.simulate_taleo(request.resume_text, request.resume_metadata)
        elif platform_lower == 'workday':
            result = simulator.simulate_workday(request.resume_text, request.resume_metadata)
        else:  # greenhouse
            result = simulator.simulate_greenhouse(request.resume_text, request.resume_metadata)

        return {
            "success": True,
            "platform": platform,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Platform simulation failed: {str(e)}"
        )


@router.post("/skills-analysis")
async def analyze_skills_categorization(request: SkillsAnalysisRequest) -> Dict[str, Any]:
    """
    Categorize skills into Hard Skills and Soft Skills.

    If job description is provided, calculates match rates for each category.

    Returns:
    - Hard skills found in resume
    - Soft skills found in resume
    - Match rates (if job description provided)
    - Missing skills recommendations
    """
    try:
        result = analyze_skills(
            request.resume_text,
            request.job_description
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Skills analysis failed: {str(e)}"
        )


@router.post("/heat-map")
async def generate_heat_map_data(request: HeatMapRequest) -> Dict[str, Any]:
    """
    Generate keyword heat map data for visual highlighting.

    Returns:
    - Matched keywords with similarity scores
    - Missing keywords
    - Overall match rate
    - Keyword positions (for highlighting)

    Frontend can use this data to color-code resume text:
    - Green: >0.8 similarity
    - Yellow: 0.5-0.8 similarity
    - No highlight: <0.5 similarity
    """
    try:
        matcher = SemanticKeywordMatcher()
        result = matcher.get_keyword_matches_detailed(
            resume_text=request.resume_text,
            job_description=request.job_description,
            threshold=request.threshold
        )

        return {
            "success": True,
            "data": result,
            "threshold": request.threshold,
            "color_mapping": {
                "high_match": ">0.8 similarity (green)",
                "moderate_match": "0.5-0.8 similarity (yellow)",
                "low_match": "<0.5 similarity (no highlight)"
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Heat map generation failed: {str(e)}"
        )


@router.post("/confidence-intervals")
async def calculate_confidence_intervals(request: ConfidenceRequest) -> Dict[str, Any]:
    """
    Add confidence intervals to scores.

    Provides statistical confidence ranges for scores, showing uncertainty.

    Example:
    - Score: 78
    - Confidence Interval: [73, 83]
    - Text: "78 ± 5 points (95% confidence)"

    Returns confidence data for all provided scores.
    """
    try:
        result = add_confidence_intervals(
            request.scores,
            request.sample_sizes
        )

        return {
            "success": True,
            "confidence_level": "95%",
            "data": result,
            "explanation": "We are 95% confident that the true scores fall within the provided ranges."
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Confidence calculation failed: {str(e)}"
        )


@router.post("/comprehensive-analysis")
async def comprehensive_phase2_analysis(
    resume_text: str,
    job_description: Optional[str] = None,
    resume_metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Run all Phase 2 analyses in one request.

    Returns:
    - ATS compatibility (all platforms)
    - Skills categorization (hard/soft)
    - Heat map data (if job description provided)
    - Confidence intervals for all scores

    This is a convenience endpoint for getting all Phase 2 features at once.
    """
    try:
        results = {}

        # 1. ATS Simulation
        results['ats_compatibility'] = analyze_ats_compatibility(
            resume_text,
            resume_metadata or {}
        )

        # 2. Skills Categorization
        results['skills_analysis'] = analyze_skills(
            resume_text,
            job_description
        )

        # 3. Heat Map Data (if job description provided)
        if job_description:
            matcher = SemanticKeywordMatcher()
            results['heat_map'] = matcher.get_keyword_matches_detailed(
                resume_text=resume_text,
                job_description=job_description,
                threshold=0.7
            )

        # 4. Confidence Intervals for ATS scores
        ats_scores = {
            'overall_ats_score': results['ats_compatibility']['overall_score']
        }

        # Add platform-specific scores
        for platform_name, platform_data in results['ats_compatibility']['platforms'].items():
            ats_scores[f'{platform_name.lower()}_score'] = platform_data['pass_probability']

        # Calculate confidence intervals
        scorer = ConfidenceScorer()
        confidence_data = {}

        for score_name, score_value in ats_scores.items():
            confidence = scorer.calculate_with_confidence(score_value, sample_size=30)
            confidence_data[score_name] = {
                'score': confidence.score,
                'confidence_interval': [confidence.confidence_lower, confidence.confidence_upper],
                'margin_of_error': confidence.margin_of_error,
                'text': confidence.confidence_text,
                'reliability': confidence.reliability_rating
            }

        results['confidence_intervals'] = confidence_data

        # 5. Add skills match confidence (if job description provided)
        if job_description and 'hard_skills_analysis' in results['skills_analysis']:
            hard_match_rate = results['skills_analysis']['hard_skills_analysis']['match_rate']
            soft_match_rate = results['skills_analysis']['soft_skills_analysis']['match_rate']

            hard_confidence = scorer.calculate_with_confidence(hard_match_rate, sample_size=20)
            soft_confidence = scorer.calculate_with_confidence(soft_match_rate, sample_size=15)

            results['confidence_intervals']['hard_skills_match'] = {
                'score': hard_confidence.score,
                'confidence_interval': [hard_confidence.confidence_lower, hard_confidence.confidence_upper],
                'text': hard_confidence.confidence_text
            }

            results['confidence_intervals']['soft_skills_match'] = {
                'score': soft_confidence.score,
                'confidence_interval': [soft_confidence.confidence_lower, soft_confidence.confidence_upper],
                'text': soft_confidence.confidence_text
            }

        return {
            "success": True,
            "data": results,
            "metadata": {
                "phase": "Phase 2: Core Features",
                "features": [
                    "ATS Platform Simulation",
                    "Hard/Soft Skills Categorization",
                    "Keyword Heat Map",
                    "Confidence Scoring"
                ]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comprehensive analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for Phase 2 features"""
    return {
        "status": "healthy",
        "phase": "Phase 2",
        "features": "ATS Simulation, Skills Categorization, Heat Map, Confidence Scoring"
    }
