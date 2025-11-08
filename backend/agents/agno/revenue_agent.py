"""
REVENUE Agent - Revenue prediction specialist

Predicts restaurant revenue potential based on all factors with reasoning.
"""

from agno import Agent
from typing import Dict, Any
import os


class RevenueAgent(Agent):
    """
    Specialist agent for revenue prediction with reasoning

    Uses Agno reasoning to synthesize all factors (demographics, competition,
    transit, etc.) and predict revenue potential with confidence levels.

    THIS IS THE CORE VALUE PROPOSITION - THE AGENT THAT MAKES THE FINAL CALL.
    """

    def __init__(self):
        super().__init__(
            name="REVENUE",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are a revenue prediction specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Synthesize all factors (demographics, competition, transit, location)\n"
                "2. Predict monthly revenue potential with reasoning\n"
                "3. Calculate overall opportunity score (0-100)\n"
                "4. Provide confidence intervals and risk-adjusted predictions\n"
                "5. Explain the 'why' behind predictions with transparent reasoning\n\n"
                "This is the final decision-making agent. Your predictions directly impact "
                "business success. Always show your work and reasoning."
            ),
            instructions=[
                "Synthesize inputs from GEO, DEMO, COMP, TRANSIT agents",
                "Weight factors based on restaurant concept type",
                "Predict monthly revenue with reasoning",
                "Calculate opportunity score (0-100)",
                "Provide confidence intervals (optimistic, realistic, pessimistic)",
                "Explain key drivers of prediction",
                "Show reasoning traces for transparency",
                "Account for concept-specific factors (fine dining vs quick service)",
            ],
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def predict_revenue(
        self,
        concept: str,
        geo_results: Dict[str, Any],
        demo_results: Dict[str, Any],
        comp_results: Dict[str, Any],
        transit_results: Dict[str, Any],
        risk_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict restaurant revenue potential with reasoning

        Args:
            concept: Restaurant concept type
            geo_results: GEO agent results
            demo_results: DEMO agent results
            comp_results: COMP agent results
            transit_results: TRANSIT agent results
            risk_results: RISK agent results

        Returns:
            {
                "opportunity_score": 87,
                "predicted_monthly_revenue": 145000,
                "revenue_confidence": "high",
                "revenue_range": {
                    "pessimistic": 95000,
                    "realistic": 145000,
                    "optimistic": 185000
                },
                "key_drivers": [
                    {
                        "factor": "Demographics",
                        "impact": "positive",
                        "weight": 0.35,
                        "score": 85,
                        "description": "Median income €48k matches target market"
                    },
                    {
                        "factor": "Competition",
                        "impact": "neutral",
                        "weight": 0.25,
                        "score": 72,
                        "description": "Moderate saturation, good differentiation potential"
                    },
                    ...
                ],
                "reasoning": "Detailed revenue prediction reasoning...",
                "prediction_breakdown": {
                    "base_revenue": 120000,
                    "demographic_adjustment": +15000,
                    "competition_adjustment": -5000,
                    "transit_adjustment": +10000,
                    "location_quality_adjustment": +5000
                }
            }
        """
        # Extract scores
        demo_score = demo_results.get("demographic_score", 70)
        comp_score = comp_results.get("competition_score", 70)
        transit_score = transit_results.get("transit_score", 70)
        confidence = risk_results.get("overall_confidence", 70)

        # Extract key data
        population_density = demo_results.get("population_density", 0)
        median_income = demo_results.get("median_income", 45000)
        competitor_count = comp_results.get("competitor_count", 0)
        competitors_per_1k = comp_results.get("competitors_per_1k", 0)
        transit_rating = transit_results.get("transit_access_rating", "fair")

        # Concept-specific parameters
        concept_params = self._get_concept_parameters(concept)

        # Build agent prompt
        prompt = f"""
        Predict monthly revenue for a {concept.replace('_', ' ')} restaurant based on comprehensive site analysis:

        SYNTHESIS OF ALL FACTORS:

        Demographics (Score: {demo_score}/100):
        - Population Density: {population_density:,}/km²
        - Median Income: €{median_income:,}
        - Income Fit: {demo_results.get('income_fit', 'unknown')}
        - Age Fit: {demo_results.get('age_fit', 'unknown')}

        Competition (Score: {comp_score}/100):
        - Competitors: {competitor_count} in 1km
        - Saturation: {comp_results.get('saturation_level', 'unknown')} ({competitors_per_1k:.2f} per 1k residents)
        - Competitive Pressure: {comp_results.get('competitive_pressure', 'unknown')}

        Transit & Access (Score: {transit_score}/100):
        - Transit Rating: {transit_rating}
        - Walkability: {transit_results.get('walkability_rating', 'unknown')}

        Location Quality:
        - Geographic Context: {geo_results.get('geographic_context', 'unknown')}
        - Overall Confidence: {confidence}/100

        CONCEPT PARAMETERS ({concept.replace('_', ' ')}):
        - Average Check: €{concept_params['avg_check']}
        - Daily Covers Target: {concept_params['daily_covers']}
        - Operating Days/Month: {concept_params['operating_days']}

        REVENUE PREDICTION REQUIRED:

        1. Base Revenue Calculation:
           - Start with concept baseline (avg check × daily covers × operating days)
           - Baseline = €{concept_params['avg_check']} × {concept_params['daily_covers']} × {concept_params['operating_days']}
           - Base = €{concept_params['avg_check'] * concept_params['daily_covers'] * concept_params['operating_days']:,}

        2. Factor Adjustments:
           - Demographics: How should {demo_score}/100 adjust revenue? (+/- %)
           - Competition: How does {comp_score}/100 affect revenue? (+/- %)
           - Transit: How does {transit_score}/100 boost/reduce revenue? (+/- %)
           - Location Quality: Premium/discount based on {geo_results.get('geographic_context')}? (+/- %)

        3. Final Monthly Revenue Prediction:
           - Apply all adjustments to base revenue
           - Provide realistic, pessimistic, and optimistic scenarios

        4. Opportunity Score (0-100):
           - Weighted synthesis of all factors
           - Demographics: 35% weight
           - Competition: 25% weight
           - Transit: 20% weight
           - Location: 20% weight

        5. Key Revenue Drivers:
           - Identify top 3-5 factors driving the prediction
           - Classify impact (positive/neutral/negative)

        6. Reasoning & Transparency:
           - Show step-by-step calculation
           - Explain assumptions
           - Highlight uncertainties

        Provide your detailed revenue prediction with transparent reasoning.
        """

        response = self.run(prompt)
        reasoning_text = response.content if hasattr(response, 'content') else str(response)

        # Calculate revenue programmatically
        base_revenue = (
            concept_params['avg_check'] *
            concept_params['daily_covers'] *
            concept_params['operating_days']
        )

        # Factor adjustments
        demo_adjustment = self._calculate_adjustment(demo_score, base_revenue, weight=0.35)
        comp_adjustment = self._calculate_adjustment(comp_score, base_revenue, weight=0.25)
        transit_adjustment = self._calculate_adjustment(transit_score, base_revenue, weight=0.20)
        location_adjustment = self._calculate_location_adjustment(
            geo_results.get('geographic_context'),
            base_revenue,
            weight=0.20
        )

        realistic_revenue = (
            base_revenue +
            demo_adjustment +
            comp_adjustment +
            transit_adjustment +
            location_adjustment
        )

        # Confidence intervals
        confidence_factor = confidence / 100
        pessimistic_revenue = realistic_revenue * (0.65 + 0.15 * confidence_factor)
        optimistic_revenue = realistic_revenue * (1.20 + 0.10 * confidence_factor)

        # Opportunity score (weighted synthesis)
        opportunity_score = (
            demo_score * 0.35 +
            comp_score * 0.25 +
            transit_score * 0.20 +
            (confidence * 0.20)
        )

        # Key drivers
        key_drivers = [
            {
                "factor": "Demographics",
                "impact": "positive" if demo_score > 75 else "neutral" if demo_score > 60 else "negative",
                "weight": 0.35,
                "score": demo_score,
                "contribution": demo_adjustment,
                "description": f"{demo_results.get('income_fit', 'Unknown')} income fit, {demo_results.get('age_fit', 'unknown')} age distribution"
            },
            {
                "factor": "Competition",
                "impact": "positive" if comp_score > 75 else "neutral" if comp_score > 60 else "negative",
                "weight": 0.25,
                "score": comp_score,
                "contribution": comp_adjustment,
                "description": f"{comp_results.get('saturation_level', 'Unknown')} saturation, {competitor_count} competitors"
            },
            {
                "factor": "Transit & Access",
                "impact": "positive" if transit_score > 75 else "neutral" if transit_score > 60 else "negative",
                "weight": 0.20,
                "score": transit_score,
                "contribution": transit_adjustment,
                "description": f"{transit_rating.title()} transit access, {transit_results.get('walkability_rating', 'unknown')} walkability"
            },
            {
                "factor": "Location Quality",
                "impact": "positive" if confidence > 75 else "neutral",
                "weight": 0.20,
                "score": confidence,
                "contribution": location_adjustment,
                "description": geo_results.get('geographic_context', 'Unknown context')
            }
        ]

        # Sort by absolute contribution
        key_drivers.sort(key=lambda x: abs(x['contribution']), reverse=True)

        return {
            "opportunity_score": round(opportunity_score, 1),
            "predicted_monthly_revenue": round(realistic_revenue, 0),
            "revenue_confidence": self._rate_confidence(confidence),
            "revenue_range": {
                "pessimistic": round(pessimistic_revenue, 0),
                "realistic": round(realistic_revenue, 0),
                "optimistic": round(optimistic_revenue, 0)
            },
            "key_drivers": key_drivers,
            "reasoning": reasoning_text,
            "prediction_breakdown": {
                "base_revenue": round(base_revenue, 0),
                "demographic_adjustment": round(demo_adjustment, 0),
                "competition_adjustment": round(comp_adjustment, 0),
                "transit_adjustment": round(transit_adjustment, 0),
                "location_quality_adjustment": round(location_adjustment, 0),
                "total_adjustments": round(
                    demo_adjustment + comp_adjustment + transit_adjustment + location_adjustment,
                    0
                )
            },
            "assumptions": {
                "average_check": concept_params['avg_check'],
                "daily_covers": concept_params['daily_covers'],
                "operating_days_per_month": concept_params['operating_days'],
                "concept": concept
            }
        }

    def _get_concept_parameters(self, concept: str) -> Dict[str, Any]:
        """Get concept-specific parameters for revenue calculation"""
        params = {
            "casual_dining": {
                "avg_check": 28,
                "daily_covers": 120,
                "operating_days": 26
            },
            "fine_dining": {
                "avg_check": 85,
                "daily_covers": 50,
                "operating_days": 24
            },
            "quick_service": {
                "avg_check": 12,
                "daily_covers": 250,
                "operating_days": 28
            }
        }

        return params.get(concept, params["casual_dining"])

    def _calculate_adjustment(self, score: float, base: float, weight: float) -> float:
        """
        Calculate revenue adjustment based on factor score

        Score 50 = neutral (0% adjustment)
        Score 100 = very positive (+50% × weight)
        Score 0 = very negative (-50% × weight)
        """
        # Normalize score to -1 to +1 range (50 = 0)
        normalized = (score - 50) / 50

        # Apply weight and calculate adjustment
        max_adjustment = base * weight
        adjustment = max_adjustment * normalized

        return adjustment

    def _calculate_location_adjustment(
        self,
        context: Optional[str],
        base: float,
        weight: float
    ) -> float:
        """Calculate location quality premium/discount"""
        multipliers = {
            "dense urban core": 1.0,
            "suburban/small city": 0.5,
            "unknown context": 0.0
        }

        multiplier = multipliers.get(context, 0.0)
        return base * weight * multiplier

    def _rate_confidence(self, confidence: float) -> str:
        """Rate revenue confidence qualitatively"""
        if confidence >= 85:
            return "very high"
        elif confidence >= 75:
            return "high"
        elif confidence >= 60:
            return "medium"
        else:
            return "low"
