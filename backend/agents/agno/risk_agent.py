"""
RISK Agent - Risk assessment and confidence scoring specialist

Evaluates data quality, confidence levels, and risk factors for site selection.
"""

from agno import Agent
from typing import Dict, Any
import os


class RiskAgent(Agent):
    """
    Specialist agent for risk assessment and confidence scoring

    Uses Agno reasoning to evaluate data quality, identify missing information,
    assess confidence levels, and flag risk factors for decision-making.
    """

    def __init__(self):
        super().__init__(
            name="RISK",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are a risk assessment specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Evaluate data quality and completeness\n"
                "2. Calculate confidence scores for predictions\n"
                "3. Identify missing data and information gaps\n"
                "4. Flag risk factors and caution areas\n"
                "5. Provide transparency for decision-making\n\n"
                "Always provide step-by-step reasoning for risk and confidence assessments."
            ),
            instructions=[
                "Assess data quality for each component (geocoding, demographics, competition, transit)",
                "Calculate overall confidence score (0-100)",
                "Identify missing data that could impact predictions",
                "Flag high-risk factors (e.g., very high competition, low foot traffic)",
                "Provide transparency warnings for users",
                "Recommend additional data collection if needed",
            ],
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def assess_risk_and_confidence(
        self,
        geo_results: Dict[str, Any],
        demo_results: Dict[str, Any],
        comp_results: Dict[str, Any],
        transit_results: Dict[str, Any],
        revenue_prediction: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess overall risk and confidence for site selection

        Args:
            geo_results: Results from GEO agent
            demo_results: Results from DEMO agent
            comp_results: Results from COMP agent
            transit_results: Results from TRANSIT agent
            revenue_prediction: Optional revenue prediction results

        Returns:
            {
                "overall_confidence": 82,
                "confidence_rating": "high",
                "data_quality_score": 88,
                "risk_level": "low",
                "missing_data": ["Crime statistics", "Traffic counts"],
                "risk_factors": [
                    {
                        "factor": "High competition",
                        "severity": "medium",
                        "description": "20+ competitors in 1km radius"
                    }
                ],
                "data_coverage": {
                    "geocoding": 95,
                    "demographics": 90,
                    "competition": 85,
                    "transit": 88
                },
                "reasoning": "Detailed risk assessment...",
                "recommendations": [
                    "Consider collecting foot traffic data",
                    "Analyze peak hours for nearby transit"
                ]
            }
        """
        # Extract confidence from each agent
        geo_confidence = geo_results.get("confidence", "medium")
        demo_confidence = demo_results.get("confidence", "medium")
        comp_confidence = comp_results.get("confidence", "medium")
        transit_confidence = transit_results.get("confidence", "medium")

        # Extract scores
        geo_quality = geo_results.get("data_quality_score", 70)
        demo_score = demo_results.get("demographic_score", 70)
        comp_score = comp_results.get("competition_score", 70)
        transit_score = transit_results.get("transit_score", 70)

        # Build agent prompt
        prompt = f"""
        Conduct a comprehensive risk and confidence assessment for this restaurant site:

        DATA QUALITY & CONFIDENCE:

        GEO Agent:
        - Confidence: {geo_confidence}
        - Data Quality: {geo_quality}/100

        DEMO Agent:
        - Confidence: {demo_confidence}
        - Demographic Score: {demo_score}/100

        COMP Agent:
        - Confidence: {comp_confidence}
        - Competition Score: {comp_score}/100
        - Competitor Count: {comp_results.get('competitor_count', 0)}
        - Saturation: {comp_results.get('saturation_level', 'unknown')}

        TRANSIT Agent:
        - Confidence: {transit_confidence}
        - Transit Score: {transit_score}/100
        - Access Rating: {transit_results.get('transit_access_rating', 'unknown')}

        ANALYSIS REQUIRED:

        1. Overall Confidence Score (0-100):
           - Weight each agent's confidence
           - Consider data completeness
           - Account for critical missing data

        2. Data Quality Assessment:
           - Score each data category (geocoding, demographics, competition, transit)
           - Identify gaps in data coverage

        3. Risk Level (low/medium/high):
           - Assess based on data quality, competition, and prediction uncertainty

        4. Risk Factors:
           - Identify specific risks (e.g., "High competition", "Limited transit access")
           - Rate severity (low/medium/high)

        5. Missing Data:
           - List critical data points that would improve confidence
           - Examples: crime statistics, foot traffic counts, parking availability

        6. Recommendations:
           - Suggest additional data to collect
           - Flag areas needing human verification

        Provide detailed reasoning for your risk and confidence assessment.
        """

        response = self.run(prompt)
        reasoning_text = response.content if hasattr(response, 'content') else str(response)

        # Calculate overall confidence
        confidence_scores = {
            "high": 90,
            "medium": 70,
            "low": 40
        }

        avg_confidence = sum([
            confidence_scores.get(geo_confidence, 70),
            confidence_scores.get(demo_confidence, 70),
            confidence_scores.get(comp_confidence, 70),
            confidence_scores.get(transit_confidence, 70)
        ]) / 4

        # Adjust based on data quality
        data_quality_avg = (geo_quality + demo_score + comp_score + transit_score) / 4
        overall_confidence = (avg_confidence * 0.6) + (data_quality_avg * 0.4)

        # Identify risk factors
        risk_factors = []

        if comp_results.get("competitor_count", 0) > 20:
            risk_factors.append({
                "factor": "High competition",
                "severity": "medium",
                "description": f"{comp_results['competitor_count']} competitors in 1km radius"
            })

        if transit_results.get("transit_access_rating") == "poor":
            risk_factors.append({
                "factor": "Limited transit access",
                "severity": "medium",
                "description": "Poor public transit connectivity"
            })

        if demo_score < 60:
            risk_factors.append({
                "factor": "Demographic mismatch",
                "severity": "high",
                "description": "Demographics below target for concept"
            })

        if overall_confidence < 70:
            risk_factors.append({
                "factor": "Data quality concerns",
                "severity": "medium",
                "description": "Limited data availability affects prediction confidence"
            })

        # Identify missing data
        missing_data = []
        if not geo_results.get("postal_code"):
            missing_data.append("Postal code data")
        if demo_score < 50:
            missing_data.append("Complete demographic data")
        missing_data.extend([
            "Crime statistics",
            "Foot traffic counts",
            "Parking availability",
            "Rent/lease costs"
        ])

        # Data coverage breakdown
        data_coverage = {
            "geocoding": geo_quality,
            "demographics": min(demo_score, 100),
            "competition": min(comp_score, 100),
            "transit": min(transit_score, 100)
        }

        # Risk level
        if overall_confidence >= 80 and len(risk_factors) < 2:
            risk_level = "low"
        elif overall_confidence >= 65 and len(risk_factors) < 3:
            risk_level = "medium"
        else:
            risk_level = "high"

        # Confidence rating
        if overall_confidence >= 85:
            confidence_rating = "very high"
        elif overall_confidence >= 75:
            confidence_rating = "high"
        elif overall_confidence >= 60:
            confidence_rating = "medium"
        else:
            confidence_rating = "low"

        # Recommendations
        recommendations = []
        if transit_score < 70:
            recommendations.append("Consider collecting peak-hour foot traffic data")
        if comp_results.get("competitor_count", 0) > 15:
            recommendations.append("Conduct competitive differentiation analysis")
        if overall_confidence < 75:
            recommendations.append("Verify predictions with on-site visit and local market research")

        return {
            "overall_confidence": round(overall_confidence, 1),
            "confidence_rating": confidence_rating,
            "data_quality_score": round(data_quality_avg, 1),
            "risk_level": risk_level,
            "missing_data": missing_data[:5],  # Top 5
            "risk_factors": risk_factors,
            "data_coverage": {k: round(v, 1) for k, v in data_coverage.items()},
            "reasoning": reasoning_text,
            "recommendations": recommendations,
            "transparency_warning": self._generate_transparency_warning(
                confidence_rating,
                risk_level,
                missing_data
            )
        }

    def _generate_transparency_warning(
        self,
        confidence_rating: str,
        risk_level: str,
        missing_data: List[str]
    ) -> Optional[str]:
        """Generate transparency warning if needed"""
        if confidence_rating == "low" or risk_level == "high":
            return (
                f"⚠️ {confidence_rating.title()} confidence prediction with {risk_level} risk. "
                f"Missing data: {', '.join(missing_data[:3])}. "
                "Recommend on-site verification before final decision."
            )
        elif confidence_rating == "medium" or risk_level == "medium":
            return (
                f"Note: {confidence_rating.title()} confidence prediction. "
                "Consider additional market research to validate findings."
            )

        return None
