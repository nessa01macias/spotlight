"""
DEMO Agent - Demographics analysis specialist

Analyzes population demographics and income fit for restaurant concepts.
"""

from agno import Agent
from typing import Dict, Any, Optional
import os


class DemoAgent(Agent):
    """
    Specialist agent for demographic analysis with reasoning

    Uses Agno reasoning to analyze population demographics, income levels,
    age distribution, and education to assess target market fit.
    """

    def __init__(self):
        super().__init__(
            name="DEMO",
            model="openai:gpt-4",
            reasoning=True,
            markdown=True,
            description=(
                "You are a demographic analysis specialist for restaurant site selection in Finland. "
                "Your role is to:\n"
                "1. Analyze population density and age distribution\n"
                "2. Assess income levels and purchasing power\n"
                "3. Evaluate demographic fit for specific restaurant concepts\n"
                "4. Calculate demographic opportunity scores with confidence levels\n\n"
                "Always provide step-by-step reasoning for your demographic assessments."
            ),
            instructions=[
                "Analyze population density (optimal: 5,000-15,000 per km²)",
                "Assess median income fit for concept (fine dining vs casual)",
                "Evaluate age distribution for target demographics",
                "Consider education levels as proxy for concept sophistication",
                "Calculate demographic fit score (0-100) with reasoning",
                "Provide confidence based on data completeness",
            ],
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    async def analyze_demographics(
        self,
        postal_code: str,
        concept: str,
        demographics_data: Dict[str, Any],
        population_grid_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze demographics for restaurant concept fit

        Args:
            postal_code: Finnish postal code
            concept: Restaurant concept (e.g., "casual_dining", "fine_dining", "quick_service")
            demographics_data: Data from PAAVO (StatFin)
            population_grid_data: Data from population grid

        Returns:
            {
                "demographic_score": 85,
                "confidence": "high",
                "population_density": 8900,
                "population_density_rating": "optimal",
                "income_fit": "excellent",
                "median_income": 48000,
                "age_fit": "good",
                "target_age_percent": 68.5,
                "education_fit": "high",
                "reasoning": "Detailed step-by-step analysis...",
                "insights": [
                    "High population density (8,900/km²) ideal for foot traffic",
                    "Median income €48k matches casual dining target (€35k-€60k)",
                    "68% aged 15-64, strong working professional demographic"
                ]
            }
        """
        # Extract data
        population = demographics_data.get("population", 0) if demographics_data else 0
        density = population_grid_data.get("population_density", 0)
        median_income = demographics_data.get("median_income", 0) if demographics_data else 0
        age_15_64 = demographics_data.get("age_15_64_percent", 0) if demographics_data else 0
        higher_ed = demographics_data.get("higher_education_percent", 0) if demographics_data else 0

        # Define concept targets
        concept_profiles = {
            "casual_dining": {
                "income_min": 35000,
                "income_max": 65000,
                "density_min": 4000,
                "density_max": 15000,
                "target_age_min": 60,  # % aged 15-64
                "education_min": 35
            },
            "fine_dining": {
                "income_min": 55000,
                "income_max": 100000,
                "density_min": 3000,
                "density_max": 12000,
                "target_age_min": 55,
                "education_min": 50
            },
            "quick_service": {
                "income_min": 25000,
                "income_max": 55000,
                "density_min": 6000,
                "density_max": 20000,
                "target_age_min": 65,
                "education_min": 25
            }
        }

        profile = concept_profiles.get(concept, concept_profiles["casual_dining"])

        # Build agent prompt
        prompt = f"""
        Analyze the demographic fit for a {concept.replace('_', ' ')} restaurant:

        LOCATION DATA:
        - Postal Code: {postal_code}
        - Population: {population:,}
        - Population Density: {density:,} per km²
        - Median Income: €{median_income:,}
        - Age 15-64: {age_15_64}%
        - Higher Education: {higher_ed}%

        CONCEPT TARGETS:
        - Target Income Range: €{profile['income_min']:,} - €{profile['income_max']:,}
        - Optimal Density: {profile['density_min']:,} - {profile['density_max']:,} per km²
        - Target Working Age: {profile['target_age_min']}%+
        - Education Level: {profile['education_min']}%+

        ANALYSIS REQUIRED:
        1. Population Density Rating: Is {density:,}/km² optimal, too high, or too low?
        2. Income Fit: How well does €{median_income:,} match the target range?
        3. Age Distribution Fit: Is {age_15_64}% working-age population good for this concept?
        4. Education Fit: Does {higher_ed}% higher education indicate target sophistication?
        5. Overall Demographic Score: 0-100 based on above factors
        6. Confidence: High/Medium/Low based on data completeness

        Provide detailed reasoning for each assessment and an overall demographic opportunity score.
        """

        response = self.run(prompt)
        reasoning_text = response.content if hasattr(response, 'content') else str(response)

        # Calculate scores programmatically
        density_score = self._score_density(density, profile)
        income_score = self._score_income(median_income, profile)
        age_score = self._score_age(age_15_64, profile)
        education_score = self._score_education(higher_ed, profile)

        # Weighted overall score
        overall_score = (
            density_score * 0.30 +
            income_score * 0.35 +
            age_score * 0.20 +
            education_score * 0.15
        )

        # Generate insights
        insights = []
        if density >= profile['density_min'] and density <= profile['density_max']:
            insights.append(f"Optimal population density ({density:,}/km²) for {concept.replace('_', ' ')}")
        if median_income >= profile['income_min'] and median_income <= profile['income_max']:
            insights.append(f"Median income €{median_income:,} matches target market (€{profile['income_min']:,}-€{profile['income_max']:,})")
        if age_15_64 >= profile['target_age_min']:
            insights.append(f"{age_15_64}% working-age population provides strong target demographic")
        if higher_ed >= profile['education_min']:
            insights.append(f"{higher_ed}% higher education indicates sophisticated consumer base")

        return {
            "demographic_score": round(overall_score, 1),
            "confidence": self._assess_confidence(demographics_data, population_grid_data),
            "population_density": density,
            "population_density_rating": self._rate_density(density, profile),
            "income_fit": self._rate_income(median_income, profile),
            "median_income": median_income,
            "age_fit": self._rate_age(age_15_64, profile),
            "target_age_percent": age_15_64,
            "education_fit": self._rate_education(higher_ed, profile),
            "higher_education_percent": higher_ed,
            "reasoning": reasoning_text,
            "insights": insights
        }

    def _score_density(self, density: int, profile: Dict) -> float:
        """Score population density 0-100"""
        if density < profile['density_min']:
            gap = profile['density_min'] - density
            return max(50 - (gap / profile['density_min'] * 50), 0)
        elif density > profile['density_max']:
            gap = density - profile['density_max']
            return max(75 - (gap / profile['density_max'] * 25), 50)
        else:
            # Within range - score based on position in range
            middle = (profile['density_min'] + profile['density_max']) / 2
            distance = abs(density - middle)
            max_distance = (profile['density_max'] - profile['density_min']) / 2
            return 100 - (distance / max_distance * 10)

    def _score_income(self, income: float, profile: Dict) -> float:
        """Score income fit 0-100"""
        if income < profile['income_min']:
            gap = profile['income_min'] - income
            return max(50 - (gap / profile['income_min'] * 50), 0)
        elif income > profile['income_max']:
            gap = income - profile['income_max']
            return max(80 - (gap / profile['income_max'] * 30), 60)
        else:
            middle = (profile['income_min'] + profile['income_max']) / 2
            distance = abs(income - middle)
            max_distance = (profile['income_max'] - profile['income_min']) / 2
            return 100 - (distance / max_distance * 10)

    def _score_age(self, age_percent: float, profile: Dict) -> float:
        """Score age distribution 0-100"""
        if age_percent >= profile['target_age_min']:
            bonus = min((age_percent - profile['target_age_min']) * 2, 10)
            return min(90 + bonus, 100)
        else:
            gap = profile['target_age_min'] - age_percent
            return max(70 - gap * 2, 30)

    def _score_education(self, education_percent: float, profile: Dict) -> float:
        """Score education level 0-100"""
        if education_percent >= profile['education_min']:
            bonus = min((education_percent - profile['education_min']) * 1.5, 15)
            return min(85 + bonus, 100)
        else:
            gap = profile['education_min'] - education_percent
            return max(60 - gap * 1.5, 20)

    def _rate_density(self, density: int, profile: Dict) -> str:
        """Rate density qualitatively"""
        if density < profile['density_min']:
            return "too low"
        elif density > profile['density_max']:
            return "too high"
        return "optimal"

    def _rate_income(self, income: float, profile: Dict) -> str:
        """Rate income fit qualitatively"""
        if income < profile['income_min']:
            return "below target"
        elif income > profile['income_max']:
            return "above target"
        return "excellent"

    def _rate_age(self, age_percent: float, profile: Dict) -> str:
        """Rate age distribution qualitatively"""
        if age_percent >= profile['target_age_min']:
            return "excellent"
        elif age_percent >= profile['target_age_min'] - 5:
            return "good"
        return "below target"

    def _rate_education(self, education_percent: float, profile: Dict) -> str:
        """Rate education level qualitatively"""
        if education_percent >= profile['education_min']:
            return "high"
        elif education_percent >= profile['education_min'] - 10:
            return "moderate"
        return "low"

    def _assess_confidence(self, demographics_data: Optional[Dict], population_data: Optional[Dict]) -> str:
        """Assess confidence based on data availability"""
        if not demographics_data and not population_data:
            return "low"
        elif demographics_data and population_data:
            return "high"
        return "medium"
