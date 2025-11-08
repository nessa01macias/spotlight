"""
COMP Agent - Competition analysis specialist

Analyzes competitor density, saturation, and market gaps.
"""

from agno import Agent
from typing import Dict, Any, List
import os


class CompAgent(Agent):
    """
    Specialist agent for competition analysis with reasoning

    Uses Agno reasoning to analyze competitor density, market saturation,
    and identify market gaps and competitive advantages.
    """

    def __init__(self):
        super().__init__(
            name="COMP",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are a competitive analysis specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Analyze competitor density and saturation levels\n"
                "2. Assess market gaps and differentiation opportunities\n"
                "3. Evaluate competitive pressure and positioning\n"
                "4. Calculate competition scores with confidence levels\n\n"
                "Always provide step-by-step reasoning for competitive assessments."
            ),
            instructions=[
                "Count competitors within 1km radius",
                "Calculate competitors per 1,000 residents (saturation metric)",
                "Identify closest competitor distances",
                "Assess market saturation (low/medium/high)",
                "Identify gaps in market (e.g., no fine dining, no vegan options)",
                "Calculate competition score (0-100, where higher = less competition)",
                "Provide confidence based on data completeness",
            ],
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def analyze_competition(
        self,
        concept: str,
        competitors: List[Dict[str, Any]],
        population: int
    ) -> Dict[str, Any]:
        """
        Analyze competition for restaurant concept

        Args:
            concept: Restaurant concept type
            competitors: List of competitor data from OSM
            population: Population in area (for saturation calculation)

        Returns:
            {
                "competition_score": 72,
                "confidence": "high",
                "competitor_count": 12,
                "saturation_level": "moderate",
                "competitors_per_1k": 4.2,
                "nearest_competitor_m": 180,
                "competitive_pressure": "medium",
                "market_gaps": ["No vegan-focused restaurants", "Limited late-night options"],
                "reasoning": "Detailed competitive analysis...",
                "insights": [
                    "12 competitors within 1km indicates moderate saturation",
                    "Nearest competitor 180m away - manageable separation",
                    "Market gap: No dedicated vegan restaurants"
                ]
            }
        """
        competitor_count = len(competitors)
        competitors_per_1k = (competitor_count / (population / 1000)) if population > 0 else 0

        # Find nearest competitor
        nearest_distance = min(
            [c.get("distance_m", 9999) for c in competitors]
        ) if competitors else None

        # Build agent prompt
        prompt = f"""
        Analyze the competitive landscape for a {concept.replace('_', ' ')} restaurant:

        COMPETITION DATA:
        - Total Competitors in 1km: {competitor_count}
        - Population in Area: {population:,}
        - Competitors per 1,000 residents: {competitors_per_1k:.2f}
        - Nearest Competitor: {nearest_distance}m away

        COMPETITOR DETAILS:
        {self._format_competitors(competitors[:10])}

        ANALYSIS REQUIRED:
        1. Saturation Assessment: Is {competitors_per_1k:.2f} competitors/1k low, moderate, or high saturation?
           (Guidelines: <2 = low, 2-5 = moderate, >5 = high)

        2. Competitive Pressure: Based on competitor count and nearest distance, what's the competitive pressure?
           (low/medium/high)

        3. Market Gaps: What types of restaurants or cuisines are missing from the competition list?

        4. Differentiation Opportunities: How can a {concept.replace('_', ' ')} stand out in this market?

        5. Competition Score: Rate from 0-100, where:
           - 90-100: Minimal competition, strong opportunity
           - 70-89: Moderate competition, good opportunity
           - 50-69: Significant competition, requires strong differentiation
           - <50: Saturated market, challenging

        6. Confidence: Rate your confidence (high/medium/low) based on data completeness

        Provide detailed reasoning for your competitive assessment.
        """

        response = self.run(prompt)
        reasoning_text = response.content if hasattr(response, 'content') else str(response)

        # Calculate scores programmatically
        saturation_level = self._assess_saturation(competitors_per_1k)
        competition_score = self._calculate_competition_score(
            competitor_count,
            competitors_per_1k,
            nearest_distance,
            population
        )
        competitive_pressure = self._assess_pressure(competitor_count, nearest_distance)

        # Identify market gaps
        market_gaps = self._identify_gaps(competitors, concept)

        # Generate insights
        insights = []
        if competitor_count < 10:
            insights.append(f"{competitor_count} competitors indicates relatively low saturation")
        elif competitor_count < 20:
            insights.append(f"{competitor_count} competitors shows moderate market development")
        else:
            insights.append(f"{competitor_count} competitors suggests highly competitive market")

        if nearest_distance and nearest_distance > 300:
            insights.append(f"Nearest competitor {nearest_distance}m away provides good separation")
        elif nearest_distance and nearest_distance < 150:
            insights.append(f"Nearest competitor only {nearest_distance}m away - close proximity")

        if market_gaps:
            insights.append(f"Market gap identified: {market_gaps[0]}")

        return {
            "competition_score": round(competition_score, 1),
            "confidence": "high" if population > 0 and competitors else "medium",
            "competitor_count": competitor_count,
            "saturation_level": saturation_level,
            "competitors_per_1k": round(competitors_per_1k, 2),
            "nearest_competitor_m": nearest_distance,
            "competitive_pressure": competitive_pressure,
            "market_gaps": market_gaps,
            "reasoning": reasoning_text,
            "insights": insights,
            "top_competitors": competitors[:5]  # Top 5 closest
        }

    def _format_competitors(self, competitors: List[Dict]) -> str:
        """Format competitor list for prompt"""
        if not competitors:
            return "No competitor data available"

        formatted = []
        for i, comp in enumerate(competitors, 1):
            name = comp.get("name", "Unknown")
            cuisine = comp.get("cuisine", "N/A")
            distance = comp.get("distance_m", 0)
            formatted.append(f"{i}. {name} ({cuisine}) - {distance}m away")

        return "\n".join(formatted)

    def _assess_saturation(self, competitors_per_1k: float) -> str:
        """Assess market saturation level"""
        if competitors_per_1k < 2:
            return "low"
        elif competitors_per_1k < 5:
            return "moderate"
        else:
            return "high"

    def _calculate_competition_score(
        self,
        count: int,
        per_1k: float,
        nearest_distance: Optional[int],
        population: int
    ) -> float:
        """
        Calculate competition score 0-100

        Higher score = less competition = better opportunity
        """
        # Base score from saturation (inverted)
        if per_1k < 2:
            saturation_score = 90
        elif per_1k < 3:
            saturation_score = 75
        elif per_1k < 5:
            saturation_score = 60
        elif per_1k < 7:
            saturation_score = 45
        else:
            saturation_score = 30

        # Bonus for distance to nearest competitor
        distance_bonus = 0
        if nearest_distance:
            if nearest_distance > 500:
                distance_bonus = 10
            elif nearest_distance > 300:
                distance_bonus = 5
            elif nearest_distance < 100:
                distance_bonus = -10

        # Penalty for very high absolute count
        count_penalty = 0
        if count > 25:
            count_penalty = 15
        elif count > 20:
            count_penalty = 10
        elif count > 15:
            count_penalty = 5

        score = saturation_score + distance_bonus - count_penalty
        return max(min(score, 100), 0)  # Clamp 0-100

    def _assess_pressure(self, count: int, nearest_distance: Optional[int]) -> str:
        """Assess overall competitive pressure"""
        if count < 8 and (not nearest_distance or nearest_distance > 300):
            return "low"
        elif count > 20 or (nearest_distance and nearest_distance < 150):
            return "high"
        return "medium"

    def _identify_gaps(self, competitors: List[Dict], concept: str) -> List[str]:
        """Identify market gaps based on competitor types"""
        gaps = []

        # Extract cuisines/types from competitors
        cuisines = {c.get("cuisine", "").lower() for c in competitors if c.get("cuisine")}

        # Check for common gaps
        gap_checks = {
            "No vegan-focused restaurants": "vegan" not in cuisines,
            "No fine dining options": "fine_dining" not in cuisines,
            "Limited Asian cuisine": not any(c in cuisines for c in ["asian", "chinese", "japanese", "thai"]),
            "No Mediterranean restaurants": not any(c in cuisines for c in ["mediterranean", "greek", "italian"]),
            "Limited breakfast/brunch spots": "breakfast" not in cuisines and "brunch" not in cuisines,
        }

        for gap, is_gap in gap_checks.items():
            if is_gap:
                gaps.append(gap)

        return gaps[:3]  # Return top 3 gaps
