"""
Concept Management API
Allows customers to create, view, update their own restaurant concept models
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field

from models.db_init import get_db
from models.database import Concept, Customer

router = APIRouter(prefix="/api/concepts", tags=["concepts"])


# ============= Request/Response Schemas =============

class ConceptWeights(BaseModel):
    """Scoring weights for concept"""
    population: float = Field(..., ge=0, le=1)
    income: float = Field(..., ge=0, le=1)
    access: float = Field(..., ge=0, le=1)
    competition: float = Field(..., ge=0, le=1)
    walkability: float = Field(..., ge=0, le=1)


class ConceptCreate(BaseModel):
    """Create new concept"""
    customer_id: str
    name: str
    category: str  # QSR, Coffee, FastCasual, etc.
    description: Optional[str] = None
    base_revenue_eur: int = Field(..., gt=0)
    target_income_min: int = Field(..., gt=0)
    target_income_max: int = Field(..., gt=0)
    optimal_population_density: int = Field(..., gt=0)
    target_competitors_per_1k: float = Field(..., gt=0)
    weights: ConceptWeights


class ConceptUpdate(BaseModel):
    """Update concept (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    base_revenue_eur: Optional[int] = None
    target_income_min: Optional[int] = None
    target_income_max: Optional[int] = None
    optimal_population_density: Optional[int] = None
    target_competitors_per_1k: Optional[float] = None
    weights: Optional[ConceptWeights] = None
    is_active: Optional[bool] = None


class ConceptResponse(BaseModel):
    """Concept response"""
    id: str
    customer_id: str
    name: str
    category: str
    description: Optional[str]
    base_revenue_eur: int
    revenue_variance: float
    target_income_min: int
    target_income_max: int
    optimal_population_density: int
    target_competitors_per_1k: float
    weights: dict
    outcomes_count: int
    avg_prediction_error: Optional[float]
    is_system_default: bool
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ConceptListResponse(BaseModel):
    """List of concepts with metadata"""
    concepts: List[ConceptResponse]
    total: int
    system_defaults: int
    custom_concepts: int


# ============= Endpoints =============

@router.get("/", response_model=ConceptListResponse)
async def list_concepts(
    customer_id: Optional[str] = None,
    category: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all concepts
    - Filter by customer_id to see customer's concepts
    - Filter by category (QSR, Coffee, etc.)
    - Filter by is_active
    """
    query = db.query(Concept)
    
    if customer_id:
        query = query.filter(Concept.customer_id == customer_id)
    
    if category:
        query = query.filter(Concept.category == category)
    
    if is_active is not None:
        query = query.filter(Concept.is_active == is_active)
    
    concepts = query.all()
    
    # Count system defaults vs custom
    system_defaults = sum(1 for c in concepts if c.is_system_default)
    custom_concepts = len(concepts) - system_defaults
    
    return ConceptListResponse(
        concepts=[ConceptResponse.model_validate(c) for c in concepts],
        total=len(concepts),
        system_defaults=system_defaults,
        custom_concepts=custom_concepts
    )


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept(
    concept_id: str,
    db: Session = Depends(get_db)
):
    """Get single concept by ID"""
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    
    return ConceptResponse.model_validate(concept)


@router.post("/", response_model=ConceptResponse)
async def create_concept(
    concept_data: ConceptCreate,
    db: Session = Depends(get_db)
):
    """
    Create new concept for customer
    
    This allows customers to define their own unit economics and scoring weights
    """
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == concept_data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {concept_data.customer_id} not found")
    
    # Validate weights sum to approximately 1.0
    weights_dict = concept_data.weights.model_dump()
    total_weight = sum(weights_dict.values())
    if not (0.95 <= total_weight <= 1.05):
        raise HTTPException(
            status_code=400,
            detail=f"Weights must sum to approximately 1.0 (got {total_weight})"
        )
    
    # Create concept
    new_concept = Concept(
        customer_id=concept_data.customer_id,
        name=concept_data.name,
        category=concept_data.category,
        description=concept_data.description,
        base_revenue_eur=concept_data.base_revenue_eur,
        revenue_variance=0.2,  # Default ±20%, will shrink with learning
        target_income_min=concept_data.target_income_min,
        target_income_max=concept_data.target_income_max,
        optimal_population_density=concept_data.optimal_population_density,
        target_competitors_per_1k=concept_data.target_competitors_per_1k,
        weights=weights_dict,
        is_system_default=False,
        is_active=True
    )
    
    db.add(new_concept)
    db.commit()
    db.refresh(new_concept)
    
    return ConceptResponse.model_validate(new_concept)


@router.patch("/{concept_id}", response_model=ConceptResponse)
async def update_concept(
    concept_id: str,
    updates: ConceptUpdate,
    db: Session = Depends(get_db)
):
    """
    Update concept parameters
    
    Note: System defaults cannot be modified
    """
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    
    if concept.is_system_default:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify system default concepts. Clone it first."
        )
    
    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    
    if "weights" in update_data and update_data["weights"]:
        # Validate weights if provided
        weights_dict = update_data["weights"]
        total_weight = sum(weights_dict.values())
        if not (0.95 <= total_weight <= 1.05):
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to approximately 1.0 (got {total_weight})"
            )
    
    for field, value in update_data.items():
        setattr(concept, field, value)
    
    db.commit()
    db.refresh(concept)
    
    return ConceptResponse.model_validate(concept)


@router.post("/{concept_id}/clone", response_model=ConceptResponse)
async def clone_concept(
    concept_id: str,
    new_name: str,
    customer_id: str,
    db: Session = Depends(get_db)
):
    """
    Clone a concept (useful for customizing system defaults)
    
    Example: Clone "QSR" system default → "Burger King Finland QSR"
    """
    source_concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    if not source_concept:
        raise HTTPException(status_code=404, detail=f"Source concept {concept_id} not found")
    
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    # Create clone
    cloned_concept = Concept(
        customer_id=customer_id,
        name=new_name,
        category=source_concept.category,
        description=f"Cloned from {source_concept.name}",
        base_revenue_eur=source_concept.base_revenue_eur,
        revenue_variance=source_concept.revenue_variance,
        target_income_min=source_concept.target_income_min,
        target_income_max=source_concept.target_income_max,
        optimal_population_density=source_concept.optimal_population_density,
        target_competitors_per_1k=source_concept.target_competitors_per_1k,
        weights=source_concept.weights,
        is_system_default=False,
        is_active=True
    )
    
    db.add(cloned_concept)
    db.commit()
    db.refresh(cloned_concept)
    
    return ConceptResponse.model_validate(cloned_concept)


@router.delete("/{concept_id}")
async def delete_concept(
    concept_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete concept (sets is_active=False)
    
    System defaults cannot be deleted
    """
    concept = db.query(Concept).filter(Concept.id == concept_id).first()
    
    if not concept:
        raise HTTPException(status_code=404, detail=f"Concept {concept_id} not found")
    
    if concept.is_system_default:
        raise HTTPException(
            status_code=403,
            detail="Cannot delete system default concepts"
        )
    
    # Soft delete
    concept.is_active = False
    db.commit()
    
    return {"status": "deleted", "concept_id": concept_id}

