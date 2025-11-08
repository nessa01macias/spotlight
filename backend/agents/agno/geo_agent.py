"""
GEO Agent - Geocoding and location validation specialist

Handles address parsing, coordinates validation, and geographic context.
"""

from agno import Agent
from typing import Dict, Any, Optional
import os


class GeoAgent(Agent):
    """
    Specialist agent for geocoding and location validation

    Uses Agno reasoning to validate addresses, geocode locations,
    and provide geographic context for site selection.
    """

    def __init__(self):
        super().__init__(
            name="GEO",
            model="openai:gpt-4",
            reasoning=True,  # Enable chain-of-thought reasoning
            markdown=True,
            description=(
                "You are a geographic intelligence specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Validate and geocode addresses using Digitransit API\n"
                "2. Extract postal codes and municipality information\n"
                "3. Assess geographic context (urban density, proximity to landmarks)\n"
                "4. Provide confidence scores for location data quality\n\n"
                "Always reason through your analysis step-by-step and explain your confidence levels."
            ),
            instructions=[
                "Validate addresses against Finnish address format (Street Name Number, Postal Code City)",
                "Use Digitransit geocoding API for accurate coordinates",
                "Extract postal code for demographic data lookup",
                "Assess urban vs suburban vs rural context",
                "Flag any ambiguous or low-confidence geocoding results",
                "Provide reasoning for geographic suitability",
            ],
        )

        # Set API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def geocode_and_validate(
        self,
        address: str,
        geocoding_service
    ) -> Dict[str, Any]:
        """
        Geocode address and provide validated location data with reasoning

        Args:
            address: Address string to geocode
            geocoding_service: DigitransitService instance

        Returns:
            {
                "address": "Mannerheimintie 1, 00100 Helsinki",
                "latitude": 60.1699,
                "longitude": 24.9384,
                "postal_code": "00100",
                "municipality": "Helsinki",
                "confidence": "high",  # high/medium/low
                "geographic_context": "dense urban core",
                "reasoning": "Address successfully geocoded with high precision...",
                "data_quality_score": 95
            }
        """
        # Step 1: Call geocoding service
        geocode_result = await geocoding_service.geocode_address(address)

        if not geocode_result:
            return {
                "address": address,
                "error": "Geocoding failed",
                "confidence": "none",
                "reasoning": f"Could not geocode address: {address}",
                "data_quality_score": 0
            }

        # Step 2: Use Agno reasoning to validate and assess context
        prompt = f"""
        Analyze this geocoded location for restaurant site selection:

        Address: {address}
        Coordinates: {geocode_result['latitude']}, {geocode_result['longitude']}
        Postal Code: {geocode_result.get('postal_code', 'N/A')}
        Municipality: {geocode_result.get('municipality', 'N/A')}
        Label: {geocode_result.get('label', 'N/A')}

        Assess:
        1. Geocoding confidence (high/medium/low based on address match quality)
        2. Geographic context (urban core, suburban, rural)
        3. Data quality score (0-100)
        4. Any concerns or flags for this location

        Provide your reasoning and assessment.
        """

        response = self.run(prompt)

        # Extract structured data from response
        # Note: In production, you'd use structured output or parse the response
        # For now, return the geocode result with agent's reasoning

        return {
            "address": address,
            "latitude": geocode_result["latitude"],
            "longitude": geocode_result["longitude"],
            "postal_code": geocode_result.get("postal_code"),
            "municipality": geocode_result.get("municipality"),
            "label": geocode_result.get("label"),
            "confidence": self._assess_confidence(geocode_result),
            "geographic_context": self._assess_context(geocode_result),
            "reasoning": response.content if hasattr(response, 'content') else str(response),
            "data_quality_score": self._calculate_quality_score(geocode_result)
        }

    def _assess_confidence(self, geocode_result: Dict[str, Any]) -> str:
        """Assess geocoding confidence based on result data"""
        if not geocode_result:
            return "none"

        # High confidence: has postal code, municipality, and label
        if (geocode_result.get("postal_code") and
            geocode_result.get("municipality") and
            geocode_result.get("label")):
            return "high"

        # Medium confidence: missing some data but has coordinates
        if geocode_result.get("latitude") and geocode_result.get("longitude"):
            return "medium"

        return "low"

    def _assess_context(self, geocode_result: Dict[str, Any]) -> str:
        """Assess geographic context based on location"""
        # Simple heuristic based on municipality
        # In production, use population density data
        municipality = geocode_result.get("municipality", "").lower()

        if municipality in ["helsinki", "espoo", "vantaa", "tampere", "turku", "oulu"]:
            return "dense urban core"
        elif municipality:
            return "suburban/small city"

        return "unknown context"

    def _calculate_quality_score(self, geocode_result: Dict[str, Any]) -> int:
        """Calculate data quality score 0-100"""
        score = 0

        if geocode_result.get("latitude") and geocode_result.get("longitude"):
            score += 50
        if geocode_result.get("postal_code"):
            score += 25
        if geocode_result.get("municipality"):
            score += 15
        if geocode_result.get("label"):
            score += 10

        return score
