"""
Concept Learner - Outcome Learning Engine
THE HEART OF THE MOAT: Improves predictions with every restaurant opening

Every time a restaurant opens and reports actual revenue:
1. Store in ConceptTrainingOutcome
2. Re-calculate concept parameters (base_revenue, weights)
3. Update prediction accuracy metrics
4. Shrink uncertainty bands

After 10+ outcomes: Concept becomes increasingly accurate for that customer
After 100+ outcomes: Concept is highly tuned to customer's specific unit economics
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
import statistics

from models.database import Concept, ConceptTrainingOutcome, Prediction


class ConceptLearner:
    """
    Learns and improves concept parameters from actual outcomes
    """
    
    MIN_OUTCOMES_FOR_TRAINING = 5  # Need at least 5 outcomes to start learning
    MIN_OUTCOMES_FOR_WEIGHTS = 20  # Need at least 20 to retrain weights
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def record_outcome(
        self,
        prediction_id: int,
        actual_revenue: float,
        opened_at: datetime
    ) -> Dict[str, Any]:
        """
        Record actual outcome and trigger learning
        
        Returns: {
            "training_outcome_id": int,
            "variance_pct": float,
            "triggered_retraining": bool,
            "new_accuracy": float (if retrained)
        }
        """
        # Get prediction
        prediction = self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        if not prediction.concept_id:
            # No concept linked - can't learn
            return {
                "training_outcome_id": None,
                "variance_pct": 0,
                "triggered_retraining": False,
                "message": "No concept linked to prediction - cannot learn"
            }
        
        # Calculate variance
        variance_pct = ((actual_revenue - prediction.revenue_mid) / prediction.revenue_mid) * 100
        
        # Store training outcome
        training_outcome = ConceptTrainingOutcome(
            concept_id=prediction.concept_id,
            prediction_id=prediction_id,
            predicted_revenue_eur=prediction.revenue_mid,
            predicted_score=prediction.score,
            features_used=prediction.features,
            actual_revenue_eur=actual_revenue,
            variance_pct=variance_pct,
            opened_at=opened_at,
            used_in_training=False,
            training_weight=1.0  # More recent outcomes can get higher weight
        )
        
        self.db.add(training_outcome)
        self.db.flush()
        
        # Update concept outcomes count
        concept = self.db.query(Concept).filter(Concept.id == prediction.concept_id).first()
        concept.outcomes_count += 1
        
        # Check if we should retrain
        triggered_retraining = False
        new_accuracy = None
        
        if concept.outcomes_count >= self.MIN_OUTCOMES_FOR_TRAINING:
            # Enough data to retrain
            self._retrain_concept(concept.id)
            triggered_retraining = True
            new_accuracy = concept.avg_prediction_error
        
        self.db.commit()
        
        return {
            "training_outcome_id": training_outcome.id,
            "variance_pct": round(variance_pct, 2),
            "triggered_retraining": triggered_retraining,
            "new_accuracy": new_accuracy,
            "outcomes_count": concept.outcomes_count
        }
    
    def _retrain_concept(self, concept_id: str):
        """
        Retrain concept parameters from all outcomes
        
        Updates:
        1. base_revenue_eur → median of actual revenues
        2. revenue_variance → shrinks as predictions get better
        3. avg_prediction_error → MAPE
        4. weights → optimize to minimize prediction error (if enough data)
        """
        concept = self.db.query(Concept).filter(Concept.id == concept_id).first()
        if not concept:
            return
        
        # Get all training outcomes
        outcomes = self.db.query(ConceptTrainingOutcome).filter(
            ConceptTrainingOutcome.concept_id == concept_id
        ).all()
        
        if len(outcomes) < self.MIN_OUTCOMES_FOR_TRAINING:
            return
        
        # 1. Update base_revenue → median of actuals
        actual_revenues = [o.actual_revenue_eur for o in outcomes]
        new_base_revenue = statistics.median(actual_revenues)
        
        # 2. Calculate prediction error (MAPE)
        absolute_percent_errors = [abs(o.variance_pct) for o in outcomes]
        mape = statistics.mean(absolute_percent_errors)
        
        # 3. Update revenue_variance (shrinks with more data and better accuracy)
        # Start at 0.20 (±20%), shrink to 0.10 (±10%) as accuracy improves
        if mape < 10:
            new_variance = 0.10  # Very accurate
        elif mape < 15:
            new_variance = 0.12
        elif mape < 20:
            new_variance = 0.15
        else:
            new_variance = max(0.20 - (len(outcomes) * 0.005), 0.15)  # Shrink slowly
        
        # Update concept
        concept.base_revenue_eur = int(new_base_revenue)
        concept.revenue_variance = new_variance
        concept.avg_prediction_error = mape
        concept.last_trained_at = datetime.utcnow()
        
        # 4. Optimize weights (if we have enough data)
        if len(outcomes) >= self.MIN_OUTCOMES_FOR_WEIGHTS:
            optimized_weights = self._optimize_weights(outcomes, concept.weights)
            if optimized_weights:
                concept.weights = optimized_weights
        
        # Mark outcomes as used in training
        for outcome in outcomes:
            outcome.used_in_training = True
        
        self.db.flush()
    
    def _optimize_weights(
        self,
        outcomes: list,
        current_weights: Dict[str, float]
    ) -> Optional[Dict[str, float]]:
        """
        Optimize scoring weights to minimize prediction error
        
        Simple approach: For each factor, calculate correlation with revenue
        Factors with higher correlation get higher weight
        
        More sophisticated approach (future): Use gradient descent or random forest feature importance
        """
        if len(outcomes) < self.MIN_OUTCOMES_FOR_WEIGHTS:
            return None
        
        # Extract features and actual revenues
        feature_names = ["population", "income", "access", "competition", "walkability"]
        feature_revenues = {name: [] for name in feature_names}
        actual_revenues = []
        
        for outcome in outcomes:
            if not outcome.features_used:
                continue
            
            actual_revenues.append(outcome.actual_revenue_eur)
            
            # Map feature values to revenue
            features = outcome.features_used
            feature_revenues["population"].append(features.get("population_density", 0))
            feature_revenues["income"].append(features.get("median_income", 0))
            feature_revenues["access"].append(
                1 / (features.get("nearest_metro_distance_m", 1000) + 1)  # Inverse distance
            )
            feature_revenues["competition"].append(
                features.get("competitors_per_1k_residents", 0)
            )
            feature_revenues["walkability"].append(
                features.get("walkability_poi_count", 0)
            )
        
        # Calculate correlation for each feature
        correlations = {}
        for name in feature_names:
            corr = self._calculate_correlation(feature_revenues[name], actual_revenues)
            correlations[name] = abs(corr)  # Use absolute value (positive or negative matters)
        
        # Normalize correlations to weights (sum to 1.0)
        total_corr = sum(correlations.values())
        if total_corr == 0:
            return None  # Can't optimize
        
        new_weights = {
            name: round(corr / total_corr, 2)
            for name, corr in correlations.items()
        }
        
        # Ensure weights sum to exactly 1.0
        weight_sum = sum(new_weights.values())
        if weight_sum != 1.0:
            # Adjust largest weight to make sum = 1.0
            max_key = max(new_weights, key=new_weights.get)
            new_weights[max_key] = round(new_weights[max_key] + (1.0 - weight_sum), 2)
        
        return new_weights
    
    def _calculate_correlation(self, x: list, y: list) -> float:
        """
        Calculate Pearson correlation coefficient
        Returns: -1 to 1 (0 = no correlation, 1 = perfect positive, -1 = perfect negative)
        """
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        # Remove None values
        pairs = [(xi, yi) for xi, yi in zip(x, y) if xi is not None and yi is not None]
        if len(pairs) < 2:
            return 0.0
        
        x_clean, y_clean = zip(*pairs)
        
        # Calculate means
        x_mean = statistics.mean(x_clean)
        y_mean = statistics.mean(y_clean)
        
        # Calculate correlation
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x_clean, y_clean))
        x_variance = sum((xi - x_mean) ** 2 for xi in x_clean)
        y_variance = sum((yi - y_mean) ** 2 for yi in y_clean)
        
        denominator = (x_variance * y_variance) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def get_concept_stats(self, concept_id: str) -> Dict[str, Any]:
        """
        Get training statistics for a concept
        """
        concept = self.db.query(Concept).filter(Concept.id == concept_id).first()
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")
        
        outcomes = self.db.query(ConceptTrainingOutcome).filter(
            ConceptTrainingOutcome.concept_id == concept_id
        ).all()
        
        if not outcomes:
            return {
                "concept_id": concept_id,
                "concept_name": concept.name,
                "outcomes_count": 0,
                "avg_prediction_error": None,
                "revenue_variance": concept.revenue_variance,
                "last_trained_at": None,
                "status": "No outcomes yet"
            }
        
        # Calculate detailed stats
        variances = [o.variance_pct for o in outcomes]
        absolute_errors = [abs(v) for v in variances]
        
        return {
            "concept_id": concept_id,
            "concept_name": concept.name,
            "outcomes_count": len(outcomes),
            "avg_prediction_error": concept.avg_prediction_error,
            "revenue_variance": concept.revenue_variance,
            "base_revenue_eur": concept.base_revenue_eur,
            "last_trained_at": concept.last_trained_at.isoformat() if concept.last_trained_at else None,
            "median_variance_pct": statistics.median(absolute_errors),
            "worst_variance_pct": max(absolute_errors),
            "best_variance_pct": min(absolute_errors),
            "within_band_count": sum(1 for e in absolute_errors if e <= concept.revenue_variance * 100),
            "weights": concept.weights,
            "status": "Learning" if len(outcomes) < 50 else "Mature"
        }

