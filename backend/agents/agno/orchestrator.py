"""
ORCHESTRATOR Agent - Multi-agent coordination for site selection

Coordinates all specialist agents and synthesizes their outputs into
a comprehensive site analysis with transparent reasoning.

THIS IS THE BRAIN OF SPOTLIGHT.
"""

from agno import Agent
from typing import Dict, Any
import os

from .geo_agent import GeoAgent
from .demo_agent import DemoAgent
from .comp_agent import CompAgent
from .transit_agent import TransitAgent
from .risk_agent import RiskAgent
from .revenue_agent import RevenueAgent


class OrchestratorAgent(Agent):
    """
    Orchestrator agent that coordinates all specialist agents

    This agent:
    1. Receives raw data from DataCollector
    2. Delegates to specialist agents (GEO, DEMO, COMP, TRANSIT, RISK, REVENUE)
    3. Synthesizes all reasoning traces
    4. Produces final comprehensive analysis

    The orchestrator provides the overall narrative and ensures
    all agents work together coherently.
    """

    def __init__(self):
        super().__init__(
            name="ORCHESTRATOR",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are the orchestrator agent for Spotlight restaurant site selection. "
                "Your role is to:\n"
                "1. Coordinate specialist agents (GEO, DEMO, COMP, TRANSIT, RISK, REVENUE)\n"
                "2. Synthesize their analyses into a coherent narrative\n"
                "3. Provide executive summary of site potential\n"
                "4. Ensure transparency and explainability\n"
                "5. Make final recommendation with confidence\n\n"
                "You are the voice of Spotlight - professional, data-driven, transparent."
            ),
            instructions=[
                "Delegate tasks to appropriate specialist agents",
                "Synthesize reasoning from all agents",
                "Identify consensus and conflicts between agents",
                "Provide clear executive summary",
                "Make final recommendation (Highly Recommended / Recommended / Consider Alternatives / Not Recommended)",
                "Ensure all reasoning is transparent and traceable",
            ],
        )

        # Initialize specialist agents
        self.geo_agent = GeoAgent()
        self.demo_agent = DemoAgent()
        self.comp_agent = CompAgent()
        self.transit_agent = TransitAgent()
        self.risk_agent = RiskAgent()
        self.revenue_agent = RevenueAgent()

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def analyze_site(
        self,
        address: str,
        concept: str,
        raw_data: Dict[str, Any],
        data_services: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate comprehensive site analysis

        Args:
            address: Restaurant address
            concept: Restaurant concept type
            raw_data: Raw data from DataCollector
            data_services: Service instances (geocoder, etc.)

        Returns:
            Complete site analysis with reasoning traces from all agents
        """
        print(f"🎯 ORCHESTRATOR: Analyzing {address} for {concept}")

        # Step 1: GEO Agent - Validate location
        print("  → GEO Agent: Geocoding and validation...")
        geo_results = await self.geo_agent.geocode_and_validate(
            address,
            data_services.get("geocoder")
        )

        # Step 2: DEMO Agent - Analyze demographics
        print("  → DEMO Agent: Demographics analysis...")
        demo_results = await self.demo_agent.analyze_demographics(
            postal_code=raw_data.get("postal_code"),
            concept=concept,
            demographics_data=raw_data.get("demographics"),
            population_grid_data=raw_data.get("population_grid")
        )

        # Step 3: COMP Agent - Analyze competition
        print("  → COMP Agent: Competition analysis...")
        comp_results = await self.comp_agent.analyze_competition(
            concept=concept,
            competitors=raw_data.get("competitors", []),
            population=raw_data.get("population_grid", {}).get("total_population", 10000)
        )

        # Step 4: TRANSIT Agent - Analyze accessibility
        print("  → TRANSIT Agent: Transit accessibility...")
        transit_results = await self.transit_agent.analyze_transit(
            transit_data=raw_data.get("transit", {}),
            walkability_poi_count=raw_data.get("walkability_poi_count", 0),
            municipality=geo_results.get("municipality", "Unknown")
        )

        # Step 5: RISK Agent - Assess risk and confidence
        print("  → RISK Agent: Risk assessment...")
        risk_results = await self.risk_agent.assess_risk_and_confidence(
            geo_results=geo_results,
            demo_results=demo_results,
            comp_results=comp_results,
            transit_results=transit_results
        )

        # Step 6: REVENUE Agent - Predict revenue
        print("  → REVENUE Agent: Revenue prediction...")
        revenue_results = await self.revenue_agent.predict_revenue(
            concept=concept,
            geo_results=geo_results,
            demo_results=demo_results,
            comp_results=comp_results,
            transit_results=transit_results,
            risk_results=risk_results
        )

        # Step 7: Orchestrator synthesis
        print("  → ORCHESTRATOR: Synthesizing final analysis...")
        synthesis = await self._synthesize_analysis(
            address=address,
            concept=concept,
            geo_results=geo_results,
            demo_results=demo_results,
            comp_results=comp_results,
            transit_results=transit_results,
            risk_results=risk_results,
            revenue_results=revenue_results
        )

        # Return complete analysis
        return {
            "address": address,
            "concept": concept,
            "opportunity_score": revenue_results["opportunity_score"],
            "predicted_monthly_revenue": revenue_results["predicted_monthly_revenue"],
            "confidence": risk_results["overall_confidence"],
            "confidence_rating": risk_results["confidence_rating"],
            "recommendation": synthesis["recommendation"],
            "executive_summary": synthesis["executive_summary"],

            # Agent results (for transparency)
            "geo_analysis": geo_results,
            "demographic_analysis": demo_results,
            "competition_analysis": comp_results,
            "transit_analysis": transit_results,
            "risk_analysis": risk_results,
            "revenue_analysis": revenue_results,

            # Synthesized insights
            "key_strengths": synthesis["key_strengths"],
            "key_concerns": synthesis["key_concerns"],
            "action_items": synthesis["action_items"],

            # Transparency
            "reasoning_traces": {
                "geo": geo_results.get("reasoning"),
                "demographics": demo_results.get("reasoning"),
                "competition": comp_results.get("reasoning"),
                "transit": transit_results.get("reasoning"),
                "risk": risk_results.get("reasoning"),
                "revenue": revenue_results.get("reasoning"),
                "orchestrator": synthesis.get("reasoning")
            }
        }

    async def _synthesize_analysis(
        self,
        address: str,
        concept: str,
        geo_results: Dict,
        demo_results: Dict,
        comp_results: Dict,
        transit_results: Dict,
        risk_results: Dict,
        revenue_results: Dict
    ) -> Dict[str, Any]:
        """Synthesize all agent results into executive summary"""

        opportunity_score = revenue_results["opportunity_score"]
        predicted_revenue = revenue_results["predicted_monthly_revenue"]
        confidence = risk_results["overall_confidence"]

        # Build synthesis prompt
        prompt = f"""
        As the Orchestrator, synthesize the complete site analysis for {address}:

        AGENT RESULTS SUMMARY:

        GEO Agent:
        - Location: {geo_results.get('label', address)}
        - Confidence: {geo_results.get('confidence')}
        - Context: {geo_results.get('geographic_context')}

        DEMO Agent:
        - Score: {demo_results.get('demographic_score')}/100
        - Population Density: {demo_results.get('population_density'):,}/km²
        - Income Fit: {demo_results.get('income_fit')}
        - Key Insight: {demo_results.get('insights', ['N/A'])[0] if demo_results.get('insights') else 'N/A'}

        COMP Agent:
        - Score: {comp_results.get('competition_score')}/100
        - Competitors: {comp_results.get('competitor_count')}
        - Saturation: {comp_results.get('saturation_level')}
        - Key Insight: {comp_results.get('insights', ['N/A'])[0] if comp_results.get('insights') else 'N/A'}

        TRANSIT Agent:
        - Score: {transit_results.get('transit_score')}/100
        - Access: {transit_results.get('transit_access_rating')}
        - Walkability: {transit_results.get('walkability_rating')}

        RISK Agent:
        - Overall Confidence: {confidence}/100
        - Risk Level: {risk_results.get('risk_level')}
        - Risk Factors: {len(risk_results.get('risk_factors', []))} identified

        REVENUE Agent:
        - Opportunity Score: {opportunity_score}/100
        - Predicted Revenue: €{predicted_revenue:,}/month
        - Revenue Confidence: {revenue_results.get('revenue_confidence')}
        - Top Driver: {revenue_results['key_drivers'][0]['factor']} ({revenue_results['key_drivers'][0]['impact']})

        SYNTHESIS REQUIRED:

        1. Recommendation (choose one):
           - "Highly Recommended" (opportunity_score >= 85, confidence >= 80)
           - "Recommended" (opportunity_score >= 70, confidence >= 65)
           - "Consider Alternatives" (opportunity_score >= 55 or confidence < 65)
           - "Not Recommended" (opportunity_score < 55)

        2. Executive Summary (2-3 sentences):
           - Overall site assessment
           - Key strengths and concerns
           - Bottom line recommendation

        3. Key Strengths (top 3):
           - What makes this site attractive?

        4. Key Concerns (top 3):
           - What are the main risks or challenges?

        5. Action Items:
           - What should the user do next?
           - Any additional research needed?

        Provide a professional, data-driven synthesis that ties all agent insights together.
        """

        response = self.run(prompt)
        synthesis_text = response.content if hasattr(response, 'content') else str(response)

        # Determine recommendation programmatically
        if opportunity_score >= 85 and confidence >= 80:
            recommendation = "Highly Recommended"
            rec_emoji = "🌟"
        elif opportunity_score >= 70 and confidence >= 65:
            recommendation = "Recommended"
            rec_emoji = "✅"
        elif opportunity_score >= 55 or confidence >= 65:
            recommendation = "Consider Alternatives"
            rec_emoji = "⚠️"
        else:
            recommendation = "Not Recommended"
            rec_emoji = "❌"

        # Extract key strengths
        key_strengths = []
        if demo_results.get('demographic_score', 0) >= 75:
            key_strengths.append(f"Strong demographics: {demo_results.get('insights', ['Good demographic fit'])[0]}")
        if comp_results.get('competition_score', 0) >= 75:
            key_strengths.append(f"Low competition: {comp_results.get('insights', ['Favorable competitive landscape'])[0]}")
        if transit_results.get('transit_score', 0) >= 75:
            key_strengths.append(f"Excellent access: {transit_results.get('insights', ['Strong transit connectivity'])[0]}")

        # Extract key concerns
        key_concerns = []
        for risk_factor in risk_results.get('risk_factors', []):
            if risk_factor['severity'] in ['high', 'medium']:
                key_concerns.append(f"{risk_factor['factor']}: {risk_factor['description']}")

        if not key_concerns:
            key_concerns.append("No major concerns identified")

        # Action items
        action_items = risk_results.get('recommendations', [])
        if not action_items:
            action_items = ["Proceed with site visit to validate findings"]

        # Executive summary
        executive_summary = (
            f"{rec_emoji} {recommendation}. "
            f"This {concept.replace('_', ' ')} location scores {opportunity_score}/100 "
            f"with {confidence:.0f}% confidence. "
            f"Predicted revenue: €{predicted_revenue:,}/month. "
            f"{key_strengths[0] if key_strengths else 'Analysis complete.'}"
        )

        return {
            "recommendation": recommendation,
            "recommendation_emoji": rec_emoji,
            "executive_summary": executive_summary,
            "key_strengths": key_strengths[:3],
            "key_concerns": key_concerns[:3],
            "action_items": action_items[:3],
            "reasoning": synthesis_text
        }
