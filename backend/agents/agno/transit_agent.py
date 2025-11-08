"""
TRANSIT Agent - Transit accessibility specialist

Analyzes public transit access and walkability for site selection.
"""

from agno import Agent
from typing import Dict, Any, List
import os


class TransitAgent(Agent):
    """
    Specialist agent for transit and accessibility analysis

    Uses Agno reasoning to analyze public transit access, walkability scores,
    and accessibility for restaurant customers.
    """

    def __init__(self):
        super().__init__(
            name="TRANSIT",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are a transit and accessibility specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Analyze public transit proximity (metro, tram, bus)\n"
                "2. Assess walkability and pedestrian accessibility\n"
                "3. Evaluate overall accessibility for target customers\n"
                "4. Calculate transit scores with confidence levels\n\n"
                "Always provide step-by-step reasoning for accessibility assessments."
            ),
            instructions=[
                "Prioritize metro and tram access (most important in Helsinki)",
                "Assess walking distance to transit (<500m is ideal)",
                "Evaluate walkability POIs (shops, offices, attractions)",
                "Consider pedestrian infrastructure quality",
                "Calculate transit accessibility score (0-100)",
                "Provide confidence based on data completeness",
            ],
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def analyze_transit(
        self,
        transit_data: Dict[str, Any],
        walkability_poi_count: int,
        municipality: str
    ) -> Dict[str, Any]:
        """
        Analyze transit accessibility and walkability

        Args:
            transit_data: Transit stops data (metro, tram, bus)
            walkability_poi_count: Number of walkability POIs in 500m
            municipality: City name

        Returns:
            {
                "transit_score": 88,
                "confidence": "high",
                "nearest_metro_m": 280,
                "nearest_tram_m": 120,
                "transit_access_rating": "excellent",
                "walkability_score": 85,
                "walkability_rating": "high",
                "accessibility_summary": "Excellent public transit access",
                "reasoning": "Detailed transit analysis...",
                "insights": [
                    "Tram stop 120m away provides excellent access",
                    "Metro station 280m ensures high connectivity",
                    "45 walkability POIs indicate vibrant pedestrian area"
                ]
            }
        """
        metro_distance = transit_data.get("nearest_metro_distance_m")
        tram_distance = transit_data.get("nearest_tram_distance_m")
        metro_stations = transit_data.get("metro_stations", [])
        tram_stops = transit_data.get("tram_stops", [])

        # Build agent prompt
        prompt = f"""
        Analyze transit accessibility for a restaurant location in {municipality}:

        TRANSIT DATA:
        - Nearest Metro: {metro_distance}m away ({len(metro_stations)} stations in 500m)
        - Nearest Tram: {tram_distance}m away ({len(tram_stops)} stops in 500m)
        - Walkability POIs in 500m: {walkability_poi_count}

        METRO STATIONS:
        {self._format_transit_stops(metro_stations)}

        TRAM STOPS:
        {self._format_transit_stops(tram_stops)}

        ANALYSIS REQUIRED:
        1. Transit Access Rating: How good is the transit accessibility?
           Guidelines:
           - Excellent: Metro/tram <200m
           - Good: Metro/tram 200-400m
           - Fair: Metro/tram 400-600m
           - Poor: Metro/tram >600m

        2. Walkability Assessment: Does {walkability_poi_count} POIs indicate good pedestrian traffic?
           Guidelines:
           - High walkability: 40+ POIs
           - Moderate: 20-40 POIs
           - Low: <20 POIs

        3. Transit Score: Rate 0-100 based on:
           - Proximity to metro/tram (most important)
           - Number of nearby transit options
           - Walkability and foot traffic indicators

        4. Accessibility for Customers: How easy is it for customers to reach this location?

        5. Confidence: Rate confidence (high/medium/low) based on data availability

        Provide detailed reasoning for your transit accessibility assessment.
        """

        response = self.run(prompt)
        reasoning_text = response.content if hasattr(response, 'content') else str(response)

        # Calculate scores programmatically
        transit_score = self._calculate_transit_score(
            metro_distance,
            tram_distance,
            len(metro_stations),
            len(tram_stops)
        )
        walkability_score = self._calculate_walkability_score(walkability_poi_count)
        transit_rating = self._rate_transit_access(metro_distance, tram_distance)
        walkability_rating = self._rate_walkability(walkability_poi_count)

        # Generate insights
        insights = []
        if tram_distance and tram_distance < 200:
            insights.append(f"Tram stop {tram_distance}m away provides excellent access")
        if metro_distance and metro_distance < 300:
            insights.append(f"Metro station {metro_distance}m ensures high connectivity")
        if walkability_poi_count > 40:
            insights.append(f"{walkability_poi_count} walkability POIs indicate vibrant pedestrian area")
        elif walkability_poi_count > 20:
            insights.append(f"{walkability_poi_count} POIs suggest moderate foot traffic")

        # Overall accessibility
        overall_score = (transit_score * 0.7) + (walkability_score * 0.3)

        return {
            "transit_score": round(overall_score, 1),
            "confidence": self._assess_confidence(transit_data, walkability_poi_count),
            "nearest_metro_m": metro_distance,
            "nearest_tram_m": tram_distance,
            "metro_stations_nearby": len(metro_stations),
            "tram_stops_nearby": len(tram_stops),
            "transit_access_rating": transit_rating,
            "walkability_score": walkability_score,
            "walkability_poi_count": walkability_poi_count,
            "walkability_rating": walkability_rating,
            "accessibility_summary": self._generate_summary(transit_rating, walkability_rating),
            "reasoning": reasoning_text,
            "insights": insights
        }

    def _format_transit_stops(self, stops: List[Dict]) -> str:
        """Format transit stops for prompt"""
        if not stops:
            return "None in range"

        formatted = []
        for i, stop in enumerate(stops, 1):
            name = stop.get("name", "Unknown")
            distance = stop.get("distance_m", 0)
            formatted.append(f"{i}. {name} - {distance}m")

        return "\n".join(formatted)

    def _calculate_transit_score(
        self,
        metro_distance: Optional[int],
        tram_distance: Optional[int],
        metro_count: int,
        tram_count: int
    ) -> float:
        """Calculate transit score 0-100"""
        score = 0

        # Metro scoring (0-50 points)
        if metro_distance is not None:
            if metro_distance < 200:
                score += 50
            elif metro_distance < 300:
                score += 45
            elif metro_distance < 400:
                score += 38
            elif metro_distance < 500:
                score += 30
            elif metro_distance < 600:
                score += 20
            else:
                score += 10

        # Tram scoring (0-40 points)
        if tram_distance is not None:
            if tram_distance < 150:
                score += 40
            elif tram_distance < 250:
                score += 35
            elif tram_distance < 350:
                score += 28
            elif tram_distance < 500:
                score += 20
            else:
                score += 10

        # Bonus for multiple options (0-10 points)
        if metro_count > 1 or tram_count > 2:
            score += min(metro_count + tram_count * 2, 10)

        return min(score, 100)

    def _calculate_walkability_score(self, poi_count: int) -> float:
        """Calculate walkability score 0-100"""
        if poi_count >= 50:
            return 100
        elif poi_count >= 40:
            return 90
        elif poi_count >= 30:
            return 75
        elif poi_count >= 20:
            return 60
        elif poi_count >= 10:
            return 45
        else:
            return max(poi_count * 3, 20)

    def _rate_transit_access(
        self,
        metro_distance: Optional[int],
        tram_distance: Optional[int]
    ) -> str:
        """Rate transit access qualitatively"""
        # Prioritize closest transit option
        best_distance = min(
            [d for d in [metro_distance, tram_distance] if d is not None],
            default=None
        )

        if best_distance is None:
            return "poor"
        elif best_distance < 200:
            return "excellent"
        elif best_distance < 400:
            return "good"
        elif best_distance < 600:
            return "fair"
        else:
            return "poor"

    def _rate_walkability(self, poi_count: int) -> str:
        """Rate walkability qualitatively"""
        if poi_count >= 40:
            return "high"
        elif poi_count >= 20:
            return "moderate"
        else:
            return "low"

    def _generate_summary(self, transit_rating: str, walkability_rating: str) -> str:
        """Generate accessibility summary"""
        transit_desc = {
            "excellent": "Excellent public transit access",
            "good": "Good public transit access",
            "fair": "Fair public transit access",
            "poor": "Limited public transit access"
        }

        walk_desc = {
            "high": "highly walkable area",
            "moderate": "moderately walkable area",
            "low": "low walkability area"
        }

        return f"{transit_desc.get(transit_rating, 'Transit access unknown')} in {walk_desc.get(walkability_rating, 'area')}"

    def _assess_confidence(self, transit_data: Dict, poi_count: int) -> str:
        """Assess confidence based on data availability"""
        has_metro = transit_data.get("nearest_metro_distance_m") is not None
        has_tram = transit_data.get("nearest_tram_distance_m") is not None
        has_walkability = poi_count > 0

        if has_metro and has_tram and has_walkability:
            return "high"
        elif (has_metro or has_tram) and has_walkability:
            return "medium"
        else:
            return "low"
