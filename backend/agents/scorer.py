"""
Scoring Engine - Deterministic heuristic model for site/area scoring
NOW USES DATABASE CONCEPTS - parameters improve with outcome learning
"""

from typing import Dict, Any, Optional
import yaml
import os
from sqlalchemy.orm import Session


class ScoringEngine:
    """
    Calculate opportunity scores for sites/areas
    
    HYBRID MODE:
    1. Try to get concept from database (learned parameters)
    2. Fall back to YAML if not found (system defaults)
    """

    def __init__(self, db_session: Optional[Session] = None):
        # Database session for concept lookup (can be provided or created lazily)
        self._db_session = db_session
        self._session_created = False
        
        # Load YAML as fallback
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "concepts.yaml")
        with open(config_path, "r") as f:
            self.yaml_concepts = yaml.safe_load(f)
    
    @property
    def db_session(self) -> Optional[Session]:
        """Lazy database session - creates on first access"""
        if self._db_session is None and not self._session_created:
            try:
                from models.db_init import SessionLocal
                self._db_session = SessionLocal()
                self._session_created = True
            except Exception as e:
                print(f"Could not create DB session: {e}")
                self._session_created = True  # Don't retry
        return self._db_session
    
    def __del__(self):
        """Clean up database session if we created it"""
        if self._session_created and self._db_session:
            try:
                self._db_session.close()
            except:
                pass

    def calculate_score(
        self,
        features: Dict[str, Any],
        concept: str,
        concept_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall score and revenue prediction

        Args:
            features: Dictionary of site features (demographics, competition, etc.)
            concept: Restaurant concept category (QSR, Coffee, etc.)
            concept_id: Optional UUID of specific concept model (for customer-specific models)

        Returns:
            {
                "score": 87.5,
                "revenue_low": 1400000,
                "revenue_mid": 1650000,
                "revenue_high": 1900000,
                "confidence": 0.84,
                "score_components": {...},
                "concept_id": "uuid..." (if from DB)
            }
        """
        # Get concept configuration
        concept_config, used_concept_id = self._get_concept_config(concept, concept_id)
        
        if concept_config is None:
            raise ValueError(f"Unknown concept: {concept}")


        # Calculate component scores
        population_score = self._calculate_population_score(
            features.get("population_density", 0),
            concept_config["optimal_population_density"]
        )

        income_score = self._calculate_income_score(
            features.get("median_income", 0),
            concept_config["target_income_min"],
            concept_config["target_income_max"]
        )

        access_score = self._calculate_access_score(
            features.get("nearest_metro_distance_m"),
            features.get("nearest_tram_distance_m")
        )

        competition_score = self._calculate_competition_score(
            features.get("competitors_per_1k_residents", 0),
            concept_config["target_competitors_per_1k"]
        )

        walkability_score = self._calculate_walkability_score(
            features.get("walkability_poi_count", 0)
        )

        # Weighted overall score
        weights = concept_config["weights"]
        overall_score = (
            weights["population"] * population_score +
            weights["income"] * income_score +
            weights["access"] * access_score +
            weights["competition"] * competition_score +
            weights["walkability"] * walkability_score
        )

        # Revenue prediction
        revenue_prediction = self._calculate_revenue(
            concept_config["base_revenue_eur"],
            features.get("population_density", 0),
            features.get("median_income", 0),
            features.get("competitors_per_1k_residents", 0),
            concept_config
        )

        # Confidence based on data completeness
        confidence = self._calculate_confidence(features)

        # Revenue band based on confidence
        revenue_mid = revenue_prediction
        band_percent = 0.15 + (0.15 * (1 - confidence))  # 15-30% band
        revenue_low = revenue_mid * (1 - band_percent)
        revenue_high = revenue_mid * (1 + band_percent)

        result = {
            "score": round(overall_score, 1),
            "revenue_low": round(revenue_low),
            "revenue_mid": round(revenue_mid),
            "revenue_high": round(revenue_high),
            "confidence": round(confidence, 2),
            "score_components": {
                "population": round(population_score, 1),
                "income": round(income_score, 1),
                "access": round(access_score, 1),
                "competition": round(competition_score, 1),
                "walkability": round(walkability_score, 1)
            }
        }
        
        # Include concept_id if from database
        if used_concept_id:
            result["concept_id"] = used_concept_id
        
        return result

    def _get_concept_config(
        self, 
        concept_category: str, 
        concept_id: Optional[str] = None
    ) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get concept configuration - tries DB first, falls back to YAML
        
        Returns: (config_dict, concept_id or None)
        """
        # Try database first
        if self.db_session:
            from models.database import Concept
            
            # If specific concept_id provided, use that
            if concept_id:
                db_concept = self.db_session.query(Concept).filter(
                    Concept.id == concept_id,
                    Concept.is_active == True
                ).first()
                
                if db_concept:
                    return self._db_concept_to_config(db_concept), db_concept.id
            
            # Otherwise, get system default for this category
            db_concept = self.db_session.query(Concept).filter(
                Concept.category == concept_category,
                Concept.is_system_default == True,
                Concept.is_active == True
            ).first()
            
            if db_concept:
                return self._db_concept_to_config(db_concept), db_concept.id
        
        # Fall back to YAML
        if concept_category in self.yaml_concepts:
            return self.yaml_concepts[concept_category], None
        
        return None, None
    
    def _db_concept_to_config(self, db_concept) -> Dict[str, Any]:
        """Convert database Concept to config dict format"""
        return {
            "name": db_concept.name,
            "base_revenue_eur": db_concept.base_revenue_eur,
            "target_income_min": db_concept.target_income_min,
            "target_income_max": db_concept.target_income_max,
            "optimal_population_density": db_concept.optimal_population_density,
            "target_competitors_per_1k": db_concept.target_competitors_per_1k,
            "weights": db_concept.weights
        }

    def _calculate_population_score(self, density: float, optimal: float) -> float:
        """
        Score based on population density
        Optimal density gets 100, scales down proportionally
        """
        if density >= optimal:
            return 100.0
        elif density <= 0:
            return 0.0
        else:
            # Linear scaling up to optimal
            return (density / optimal) * 100

    def _calculate_income_score(
        self,
        median_income: float,
        target_min: float,
        target_max: float
    ) -> float:
        """
        Score based on how well income matches concept target
        """
        if median_income < target_min:
            # Below target - penalty
            gap = target_min - median_income
            penalty = min((gap / target_min) * 100, 50)
            return max(50 - penalty, 0)
        elif median_income > target_max:
            # Above target - smaller penalty (high income not bad)
            gap = median_income - target_max
            penalty = min((gap / target_max) * 50, 25)
            return max(75 - penalty, 50)
        else:
            # Within target range - excellent
            middle = (target_min + target_max) / 2
            distance_from_middle = abs(median_income - middle)
            max_distance = (target_max - target_min) / 2
            score = 100 - (distance_from_middle / max_distance * 15)
            return max(score, 85)

    def _calculate_access_score(
        self,
        metro_distance_m: Optional[float],
        tram_distance_m: Optional[float]
    ) -> float:
        """
        Score based on public transit access
        Closer = better
        """
        score = 50  # Base score

        # Metro access bonus
        if metro_distance_m is not None:
            if metro_distance_m <= 200:
                score += 40
            elif metro_distance_m <= 500:
                score += 30
            elif metro_distance_m <= 1000:
                score += 15

        # Tram access bonus
        if tram_distance_m is not None:
            if tram_distance_m <= 100:
                score += 10
            elif tram_distance_m <= 300:
                score += 5

        return min(score, 100)

    def _calculate_competition_score(
        self,
        competitors_per_1k: float,
        target: float
    ) -> float:
        """
        Score based on competition saturation
        Target level is ideal, too few or too many reduces score
        """
        if competitors_per_1k == 0:
            # No competition might mean no demand
            return 40

        # Distance from target
        ratio = competitors_per_1k / target

        if 0.8 <= ratio <= 1.2:
            # Near target - excellent
            return 100
        elif 0.5 <= ratio < 0.8:
            # Below target - good but not perfect
            return 85
        elif 1.2 < ratio <= 1.5:
            # Slightly oversaturated
            return 75
        elif ratio > 1.5:
            # Very oversaturated
            penalty = min((ratio - 1.5) * 30, 50)
            return max(50 - penalty, 20)
        else:
            # Very undersupplied
            return 60

    def _calculate_walkability_score(self, poi_count: int) -> float:
        """
        Score based on POI density (walkability proxy)
        More POIs = more foot traffic
        """
        if poi_count >= 100:
            return 100
        elif poi_count >= 50:
            return 85
        elif poi_count >= 25:
            return 70
        elif poi_count >= 10:
            return 55
        else:
            return max(poi_count * 3, 20)

    def _calculate_revenue(
        self,
        base_revenue: float,
        population_density: float,
        median_income: float,
        competitors_per_1k: float,
        concept_config: Dict[str, Any]
    ) -> float:
        """
        Estimate annual revenue based on features
        """
        # Population multiplier
        pop_multiplier = min(population_density / concept_config["optimal_population_density"], 1.5)

        # Income multiplier
        target_mid = (concept_config["target_income_min"] + concept_config["target_income_max"]) / 2
        if median_income > 0:
            income_multiplier = 0.7 + (median_income / target_mid * 0.3)
            income_multiplier = max(min(income_multiplier, 1.3), 0.7)
        else:
            income_multiplier = 1.0

        # Competition adjustment (saturation penalty)
        target_comp = concept_config["target_competitors_per_1k"]
        if competitors_per_1k > target_comp:
            saturation_penalty = min((competitors_per_1k / target_comp - 1) * 0.3, 0.4)
        else:
            saturation_penalty = 0

        # Calculate revenue
        revenue = base_revenue * pop_multiplier * income_multiplier * (1 - saturation_penalty)

        return max(revenue, base_revenue * 0.5)  # Floor at 50% of base

    def _calculate_confidence(self, features: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness
        """
        required_fields = [
            "population_density",
            "median_income",
            "competitors_count",
            "nearest_metro_distance_m"
        ]

        present = sum(1 for field in required_fields if features.get(field) is not None)
        completeness = present / len(required_fields)

        # Start at 0.6, add up to 0.4 based on completeness
        return 0.6 + (completeness * 0.4)

    def get_recommendation(self, score: float) -> str:
        """
        Get recommendation label based on score
        """
        if score >= 85:
            return "strong"
        elif score >= 70:
            return "moderate"
        elif score >= 55:
            return "weak"
        else:
            return "pass"
