from __future__ import annotations
import json
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .orm import UserORM, PackORM
from .auth import hash_password

PACKS = [
    {
        "id": "bayes-pack",
        "title": "Bayesian Reasoning",
        "subtitle": "Probability, evidence, updating, and model criticism.",
        "level": "novice-friendly",
        "concepts": [
            {"id": "prior", "title": "Prior", "prerequisites": [], "masteryDimension": "mastery", "exerciseReward": "Prior badge earned"},
            {"id": "posterior", "title": "Posterior", "prerequisites": ["prior"], "masteryDimension": "mastery", "exerciseReward": "Posterior path opened"},
            {"id": "model-checking", "title": "Model Checking", "prerequisites": ["posterior"], "masteryDimension": "mastery", "exerciseReward": "Model-checking unlocked"}
        ],
        "onboarding": {"headline": "Start with a fast visible win", "body": "Read one short orientation, answer one guided question, and leave with your first mastery marker.", "checklist": ["Read the one-screen topic orientation", "Answer one guided exercise", "Write one explanation in your own words"]},
        "compliance": {"sources": 2, "attributionRequired": True, "shareAlikeRequired": True, "noncommercialOnly": True, "flags": ["share-alike", "noncommercial", "excluded-third-party-content"]}
    },
    {
        "id": "stats-pack",
        "title": "Introductory Statistics",
        "subtitle": "Descriptive statistics, sampling, and inference.",
        "level": "novice-friendly",
        "concepts": [
            {"id": "descriptive", "title": "Descriptive Statistics", "prerequisites": [], "masteryDimension": "mastery", "exerciseReward": "Descriptive tools unlocked"},
            {"id": "sampling", "title": "Sampling", "prerequisites": ["descriptive"], "masteryDimension": "mastery", "exerciseReward": "Sampling pathway opened"}
        ],
        "onboarding": {"headline": "Build your first useful data skill", "body": "You will learn one concept that immediately helps you summarize real data.", "checklist": ["See one worked example", "Compute one short example yourself", "Explain what the result means"]},
        "compliance": {"sources": 1, "attributionRequired": True, "shareAlikeRequired": False, "noncommercialOnly": False, "flags": []}
    }
]

def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.execute(select(UserORM).where(UserORM.username == "wesley")).scalar_one_or_none() is None:
            db.add(UserORM(username="wesley", password_hash=hash_password("demo-pass"), role="admin", is_active=True))
        for pack in PACKS:
            if db.get(PackORM, pack["id"]) is None:
                db.add(PackORM(id=pack["id"], title=pack["title"], subtitle=pack["subtitle"], level=pack["level"], data_json=json.dumps(pack), is_published=True))
        db.commit()
    print("Seeded database. Demo user: wesley / demo-pass")

if __name__ == "__main__":
    main()
