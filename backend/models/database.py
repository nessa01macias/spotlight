from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID as string for cross-database compatibility"""
    return str(uuid.uuid4())


class Customer(Base):
    """SaaS Customers (restaurant chains)"""
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)  # e.g., "Burger King Finland"
    email = Column(String, unique=True, index=True)
    
    # Subscription
    plan = Column(String, default="free")  # free, basic, pro, enterprise
    analyses_limit = Column(Integer, default=10)
    analyses_used = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    concepts = relationship("Concept", back_populates="customer")


class Concept(Base):
    """
    Restaurant concepts with learnable parameters
    THE FOUNDATION OF THE MOAT - these parameters improve with every outcome
    """
    __tablename__ = "concepts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    
    # Concept details
    name = Column(String, nullable=False)  # "Burger King QSR Model"
    category = Column(String, nullable=False, index=True)  # "QSR", "Coffee", etc.
    description = Column(Text)
    
    # Revenue model (learned from outcomes)
    base_revenue_eur = Column(Integer, nullable=False)
    revenue_variance = Column(Float, default=0.2)  # ±20% default, shrinks with learning
    
    # Target demographics (customer-specific)
    target_income_min = Column(Integer, nullable=False)
    target_income_max = Column(Integer, nullable=False)
    optimal_population_density = Column(Integer, nullable=False)
    target_competitors_per_1k = Column(Float, nullable=False)
    
    # Scoring weights (learned from outcomes)
    weights = Column(JSON, nullable=False)  # {population: 0.35, income: 0.25, ...}
    
    # Learning metadata
    outcomes_count = Column(Integer, default=0)  # How many actual openings tracked
    avg_prediction_error = Column(Float)  # MAPE (Mean Absolute Percentage Error)
    last_trained_at = Column(DateTime)  # When weights were last updated
    
    # System vs custom
    is_system_default = Column(Boolean, default=False)  # True for YAML-loaded defaults
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="concepts")
    predictions = relationship("Prediction", back_populates="concept")
    training_outcomes = relationship("ConceptTrainingOutcome", back_populates="concept")


class ConceptTrainingOutcome(Base):
    """
    Training data for concept learning
    Links outcomes to concepts for parameter optimization
    """
    __tablename__ = "concept_training_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(String, ForeignKey("concepts.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False, unique=True)
    
    # What was predicted
    predicted_revenue_eur = Column(Float, nullable=False)
    predicted_score = Column(Float, nullable=False)
    features_used = Column(JSON)  # Snapshot of features at prediction time
    
    # What actually happened
    actual_revenue_eur = Column(Float, nullable=False)
    variance_pct = Column(Float, nullable=False)  # (actual - predicted) / predicted
    opened_at = Column(DateTime)
    
    # Used for re-training
    used_in_training = Column(Boolean, default=False)
    training_weight = Column(Float, default=1.0)  # More recent = higher weight
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    concept = relationship("Concept", back_populates="training_outcomes")
    prediction = relationship("Prediction")


class User(Base):
    """User accounts"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    searches = relationship("Search", back_populates="user")


class Search(Base):
    """Search history - universal search inputs"""
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String, nullable=False)
    search_type = Column(String)  # 'discovery', 'single_site', 'comparison'
    city = Column(String)
    concept = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="searches")
    evaluations = relationship("Evaluation", back_populates="search")


class Evaluation(Base):
    """Site/area evaluations"""
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("searches.id"))
    evaluation_type = Column(String)  # 'area', 'site', 'comparison'
    city = Column(String, nullable=False)
    concept = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    search = relationship("Search", back_populates="evaluations")
    predictions = relationship("Prediction", back_populates="evaluation")


class Prediction(Base):
    """Individual site/area predictions"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"))
    concept_id = Column(String, ForeignKey("concepts.id"), nullable=True, index=True)  # NEW: Link to concept used

    # Location
    address = Column(String)
    area_name = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    postal_code = Column(String)

    # Prediction results
    score = Column(Float, nullable=False)  # 0-100
    revenue_low = Column(Float, nullable=False)
    revenue_mid = Column(Float, nullable=False)
    revenue_high = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)  # 0-1

    # Ranking (if part of comparison)
    rank = Column(Integer)

    # Features used (JSON)
    features = Column(JSON)  # demographics, competition, traffic, etc.

    # Insights
    strengths = Column(JSON)  # List of positive factors
    risks = Column(JSON)  # List of risk factors
    recommendation = Column(String)  # 'strong', 'moderate', 'weak'

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="predictions")
    outcome = relationship("Outcome", back_populates="prediction", uselist=False)
    concept = relationship("Concept", back_populates="predictions")  # NEW


class Outcome(Base):
    """Actual results after opening - THE MOAT"""
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), unique=True)

    # Actual results
    actual_revenue = Column(Float)
    opening_date = Column(DateTime)
    reported_date = Column(DateTime, default=datetime.utcnow)

    # Calculated variance
    variance_percent = Column(Float)  # (actual - predicted_mid) / predicted_mid * 100
    within_predicted_band = Column(String)  # 'yes', 'no', 'pending'

    # Notes
    notes = Column(Text)

    # Relationships
    prediction = relationship("Prediction", back_populates="outcome")


class PreScoredArea(Base):
    """Pre-calculated area scores for discovery view"""
    __tablename__ = "prescored_areas"

    id = Column(Integer, primary_key=True, index=True)

    # Location
    city = Column(String, nullable=False, index=True)
    area_id = Column(String, unique=True, index=True)  # e.g., "helsinki_kamppi"
    area_name = Column(String, nullable=False)
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)

    # Scores by concept (JSON)
    scores = Column(JSON)  # {"QSR": 87, "Coffee": 91, "FastCasual": 84, ...}

    # Features (JSON)
    features = Column(JSON)

    # Metadata
    last_updated = Column(DateTime, default=datetime.utcnow)
