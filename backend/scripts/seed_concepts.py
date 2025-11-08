"""
Seed Database with Concepts from YAML
Loads concepts.yaml as system defaults for demo/onboarding
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base, Customer, Concept

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spotlight.db")

def load_yaml_concepts():
    """Load concepts from YAML file"""
    yaml_path = os.path.join(
        os.path.dirname(__file__), 
        "..", 
        "config", 
        "concepts.yaml"
    )
    
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def seed_concepts(session):
    """Seed database with YAML concepts as system defaults"""
    
    # Create "System" customer for default concepts
    system_customer = session.query(Customer).filter(
        Customer.email == "system@spotlight.ai"
    ).first()
    
    if not system_customer:
        system_customer = Customer(
            name="Spotlight System Defaults",
            email="system@spotlight.ai",
            plan="enterprise",
            analyses_limit=999999
        )
        session.add(system_customer)
        session.flush()
        print(f"✓ Created system customer: {system_customer.id}")
    else:
        print(f"✓ System customer exists: {system_customer.id}")
    
    # Load YAML concepts
    yaml_concepts = load_yaml_concepts()
    
    concepts_created = 0
    concepts_skipped = 0
    
    for category, config in yaml_concepts.items():
        # Check if concept already exists
        existing = session.query(Concept).filter(
            Concept.customer_id == system_customer.id,
            Concept.category == category,
            Concept.is_system_default == True
        ).first()
        
        if existing:
            print(f"⊗ Skipping {category} - already exists")
            concepts_skipped += 1
            continue
        
        # Create concept from YAML
        concept = Concept(
            customer_id=system_customer.id,
            name=config["name"],
            category=category,
            description=f"System default {config['name']} concept",
            base_revenue_eur=config["base_revenue_eur"],
            revenue_variance=0.2,  # Default ±20%
            target_income_min=config["target_income_min"],
            target_income_max=config["target_income_max"],
            optimal_population_density=config["optimal_population_density"],
            target_competitors_per_1k=config["target_competitors_per_1k"],
            weights=config["weights"],
            outcomes_count=0,
            avg_prediction_error=None,
            is_system_default=True,
            is_active=True
        )
        
        session.add(concept)
        concepts_created += 1
        print(f"✓ Created concept: {category} ({config['name']})")
    
    session.commit()
    
    print(f"\n{'='*60}")
    print(f"Seed complete!")
    print(f"  Created: {concepts_created} concepts")
    print(f"  Skipped: {concepts_skipped} concepts (already exist)")
    print(f"{'='*60}")
    
    # Show all concepts
    all_concepts = session.query(Concept).all()
    print(f"\nTotal concepts in database: {len(all_concepts)}")
    for c in all_concepts:
        print(f"  - {c.category}: {c.name} (ID: {c.id[:8]}...)")


def main():
    """Run migration"""
    print("="*60)
    print("Spotlight Database Seed - Concepts from YAML")
    print("="*60)
    
    # Create engine and tables
    engine = create_engine(DATABASE_URL)
    
    print("\n1. Creating tables...")
    Base.metadata.create_all(engine)
    print("✓ Tables created/verified")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n2. Seeding concepts...")
        seed_concepts(session)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == "__main__":
    main()

