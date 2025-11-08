"""
Trust Metrics Calculator
Computes confidence, coverage, and method info for transparency
"""
from typing import Dict, Any
from datetime import datetime
from models.schemas import DataCoverage, MethodInfo


class TrustMetrics:
    """Calculate trust metrics for predictions"""
    
    @staticmethod
    def calculate_coverage(features: Dict[str, Any]) -> DataCoverage:
        """
        Calculate data coverage based on available features
        
        Returns scores 0-1 for each category:
        - 1.0 = Complete data
        - 0.7-0.9 = Good data
        - 0.4-0.6 = Partial data
        - 0.0-0.3 = Limited data
        """
        # Demographics coverage
        demo_fields = ["population_1km", "population_density", "median_income"]
        demo_present = sum(1 for f in demo_fields if features.get(f) is not None)
        demographics = demo_present / len(demo_fields)
        
        # Competition coverage
        comp_fields = ["competitors_count", "competitors_per_1k_residents"]
        comp_present = sum(1 for f in comp_fields if features.get(f) is not None)
        competition = comp_present / len(comp_fields)
        
        # Transit coverage
        transit_fields = ["nearest_metro_distance_m", "nearest_tram_distance_m", "walkability_poi_count"]
        transit_present = sum(1 for f in transit_fields if features.get(f) is not None)
        transit = transit_present / len(transit_fields)
        
        # Overall coverage (weighted average)
        overall = (demographics * 0.4 + competition * 0.3 + transit * 0.3)
        
        return DataCoverage(
            demographics=round(demographics, 2),
            competition=round(competition, 2),
            transit=round(transit, 2),
            overall=round(overall, 2)
        )
    
    @staticmethod
    def calculate_confidence(
        score_components: Dict[str, float],
        coverage: DataCoverage
    ) -> float:
        """
        Calculate prediction confidence based on:
        1. Data coverage (40% weight)
        2. Score consistency (30% weight)
        3. Feature completeness (30% weight)
        
        Returns: 0-1 confidence score
        """
        # Component 1: Data coverage (40%)
        coverage_score = coverage.overall * 0.4
        
        # Component 2: Score consistency (30%)
        # If all component scores are similar, confidence is higher
        scores = [
            score_components.get("population", 50),
            score_components.get("income", 50),
            score_components.get("access", 50),
            score_components.get("competition", 50)
        ]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Lower std dev = higher consistency
        consistency = max(0, 1 - (std_dev / 50))  # Normalize by max possible std dev
        consistency_score = consistency * 0.3
        
        # Component 3: Feature completeness (30%)
        required_features = [
            "population_1km", "median_income", "competitors_count",
            "nearest_metro_distance_m", "walkability_poi_count"
        ]
        features_present = sum(1 for f in required_features if score_components.get(f) is not None)
        completeness = features_present / len(required_features)
        completeness_score = completeness * 0.3
        
        # Total confidence
        confidence = coverage_score + consistency_score + completeness_score
        
        return round(min(confidence, 1.0), 2)
    
    @staticmethod
    def get_method_info(
        scoring_method: str = "heuristic",
        features_used: Dict[str, Any] = None
    ) -> MethodInfo:
        """
        Generate method transparency info
        """
        data_sources = []
        
        # Determine which data sources were used
        if features_used:
            if features_used.get("population_1km") or features_used.get("population_density"):
                data_sources.append("Statistics Finland Population Grid (1km)")
            if features_used.get("median_income") or features_used.get("postal_code"):
                data_sources.append("Statistics Finland PAAVO (Postal Code Demographics)")
            if features_used.get("competitors_count"):
                data_sources.append("OpenStreetMap (Competition Data)")
            if features_used.get("nearest_metro_distance_m") or features_used.get("nearest_tram_distance_m"):
                data_sources.append("OpenStreetMap (Transit Data)")
        
        # Confidence basis explanation
        if scoring_method == "heuristic":
            confidence_basis = "Based on data coverage and score component consistency"
        elif scoring_method == "agent_based":
            confidence_basis = "Based on Agno reasoning agents' confidence levels"
        else:
            confidence_basis = "Based on available data quality"
        
        return MethodInfo(
            scoring_method=scoring_method,
            data_sources=data_sources or ["Limited data available"],
            last_updated=datetime.utcnow().isoformat() + "Z",
            confidence_basis=confidence_basis
        )
    
    @staticmethod
    def generate_why_bullets(
        features: Dict[str, Any],
        score_components: Dict[str, float]
    ) -> list[str]:
        """
        Generate 3-5 bullet points explaining why this area scored as it did
        """
        bullets = []
        
        # Population
        pop = features.get("population_1km")
        if pop:
            if pop > 20000:
                bullets.append(f"High population density: {pop:,} people in 1km radius")
            elif pop > 10000:
                bullets.append(f"Moderate population: {pop:,} people in 1km radius")
            else:
                bullets.append(f"Limited population: {pop:,} people in 1km radius")
        
        # Income
        income = features.get("median_income")
        if income:
            if income > 50000:
                bullets.append(f"High median income: €{income:,}/year supports premium pricing")
            elif income > 35000:
                bullets.append(f"Median income: €{income:,}/year matches target market")
            else:
                bullets.append(f"Lower median income: €{income:,}/year may limit spending")
        
        # Transit
        metro_dist = features.get("nearest_metro_distance_m")
        tram_dist = features.get("nearest_tram_distance_m")
        if metro_dist and metro_dist < 300:
            bullets.append(f"Excellent transit: Metro station {int(metro_dist)}m away")
        elif tram_dist and tram_dist < 200:
            bullets.append(f"Good transit: Tram stop {int(tram_dist)}m away")
        
        # Competition
        comp_count = features.get("competitors_count")
        if comp_count is not None:
            if comp_count < 5:
                bullets.append(f"Low competition: Only {comp_count} competitors nearby")
            elif comp_count < 15:
                bullets.append(f"Moderate competition: {comp_count} competitors in area")
            else:
                bullets.append(f"High competition: {comp_count} competitors may dilute market")
        
        return bullets[:5]  # Max 5 bullets

