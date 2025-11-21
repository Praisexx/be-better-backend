from sqlalchemy.orm import Session
from app.models.user import User
from app.models.analysis import Analysis, AnalysisStatus
from app.utils.auth import get_password_hash
import json
from datetime import datetime, timedelta
import random

def seed_database(db: Session):
    # 1. Create User
    email = "covenantchukwudi@gmail.com"
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            hashed_password=get_password_hash("password123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {email}")
    else:
        print(f"User {email} already exists")

    # 2. Create Banking Analyses
    banking_companies = ["Chase", "Bank of America", "Wells Fargo", "Citi", "Goldman Sachs", "Morgan Stanley", "US Bank", "PNC", "Capital One", "TD Bank"]
    
    for i, company in enumerate(banking_companies):
        create_analysis(db, user.id, company, "Banking", i)

    # 3. Create Real Estate Analyses
    real_estate_companies = ["Zillow", "Redfin", "ReMax", "Coldwell Banker", "Century 21", "Keller Williams", "Compass", "eXp Realty", "Sotheby's", "Berkshire Hathaway"]
    
    for i, company in enumerate(real_estate_companies):
        create_analysis(db, user.id, company, "Real Estate", i + 10)
    
    return {"message": "Database seeded successfully with 20 analyses"}

def create_analysis(db: Session, user_id: int, company_name: str, industry: str, offset: int):
    # Generate realistic dummy data
    results = {
        "company_name": company_name,
        "industry": industry,
        "summary": f"Analysis of {company_name}'s digital marketing strategy in the {industry} sector. Strong focus on customer acquisition and brand trust.",
        "performance_metrics": {
            "ctr": round(random.uniform(1.2, 3.5), 2),
            "cpc": round(random.uniform(2.5, 8.0), 2),
            "roas": round(random.uniform(2.0, 5.0), 2),
            "conversion_rate": round(random.uniform(1.5, 4.5), 2)
        },
        "recommendations": [
            "Increase budget for high-performing keywords",
            "Optimize landing pages for mobile users",
            "Test video ads for better engagement",
            "Refine audience targeting based on demographics"
        ],
        "similar_businesses": [
            {"name": f"{company_name} Competitor A", "website": "example.com"},
            {"name": f"{company_name} Competitor B", "website": "example.com"},
            {"name": f"{company_name} Competitor C", "website": "example.com"}
        ]
    }

    analysis = Analysis(
        user_id=user_id,
        csv_filename=f"{company_name.lower().replace(' ', '_')}_data.csv",
        status=AnalysisStatus.COMPLETED,
        results_json=json.dumps(results),
        created_at=datetime.now() - timedelta(days=offset) # Spread dates out
    )
    
    db.add(analysis)
    db.commit()
