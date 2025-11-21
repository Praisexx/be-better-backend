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
            "conversion_rate": round(random.uniform(1.5, 4.5), 2),
            "total_spend": round(random.uniform(5000, 50000), 2),
            "impressions": random.randint(10000, 1000000),
            "clicks": random.randint(500, 50000)
        },
        "recommendations": [
            "Increase budget for high-performing keywords",
            "Optimize landing pages for mobile users",
            "Test video ads for better engagement",
            "Refine audience targeting based on demographics",
            "Implement retargeting campaigns for cart abandoners",
            "Experiment with lookalike audiences"
        ],
        "similar_businesses": [
            {"name": f"{company_name} Competitor A", "website": "example.com", "similarity_score": 0.95},
            {"name": f"{company_name} Competitor B", "website": "example.com", "similarity_score": 0.88},
            {"name": f"{company_name} Competitor C", "website": "example.com", "similarity_score": 0.82}
        ],
        "ai_insights": [
            f"Strong engagement from {industry} enthusiasts suggests high viral potential.",
            "Video content is outperforming static images by 40%.",
            "Mobile users account for 80% of traffic; optimize landing pages.",
            "Weekends show a 20% dip in conversion; adjust ad scheduling.",
            "Lookalike audiences are delivering the lowest CPA."
        ],
        "content_strategy": {
            "Week_1": "Focus on Brand Story and Values - Video Ads",
            "Week_2": "Highlight Customer Success Stories - Carousel Ads",
            "Week_3": "Promote Limited Time Offers - Single Image Ads",
            "Week_4": "Retargeting and Loyalty Push - Dynamic Ads"
        },
        "creative_prompts": [
            {"concept": "Problem/Solution", "prompt": f"Show a common {industry} problem and how {company_name} solves it instantly."},
            {"concept": "Social Proof", "prompt": "Video testimonial of a happy customer sharing their success story."},
            {"concept": "Behind the Scenes", "prompt": "A day in the life of the team, showcasing expertise and dedication."},
            {"concept": "Educational", "prompt": f"5 Tips for better {industry} results that most people ignore."},
            {"concept": "Urgency", "prompt": "Limited time offer highlighting exclusive benefits for new sign-ups."}
        ],
        "captions_hashtags": [
            {"text": f"Ready to transform your {industry} experience? 🚀 Join thousands of satisfied customers with {company_name}.", "hashtags": f"#{industry} #Growth #{company_name} #Success"},
            {"text": "Stop guessing, start growing. 📈 See why we are the #1 choice for smart professionals.", "hashtags": "#Business #Strategy #Results #Innovation"},
            {"text": "The secret to success? It's simpler than you think. 💡 Discover the difference today.", "hashtags": "#Tips #Advice #Expertise #Future"},
            {"text": f"Don't settle for average. You deserve the best in {industry}. 🏆", "hashtags": "#Premium #Quality #Excellence #Goals"},
            {"text": "Your journey to the top starts here. Are you ready? 🔥", "hashtags": "#Motivation #Hustle #Grind #Win"}
        ],
        "next_ad_plan": {
            "awareness": random.randint(50000, 100000),
            "interest": random.randint(20000, 40000),
            "consideration": random.randint(5000, 15000),
            "intent": random.randint(1000, 4000),
            "conversion": random.randint(200, 800)
        },
        "audience_insights": {
            "age_18_24": random.randint(10, 30),
            "age_25_34": random.randint(30, 50),
            "age_35_44": random.randint(15, 35),
            "age_45_54": random.randint(5, 20),
            "age_55_plus": random.randint(1, 10),
            "gender_male": random.randint(40, 60),
            "gender_female": random.randint(40, 60)
        }
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
