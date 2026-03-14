from __future__ import annotations
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .orm import UserORM
from .auth import hash_password
from .repository import upsert_pack
from .models import PackData, PackConcept, PackCompliance

def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.execute(select(UserORM).where(UserORM.username == "wesley")).scalar_one_or_none() is None:
            db.add(UserORM(username="wesley", password_hash=hash_password("demo-pass"), role="admin", is_active=True))
        db.commit()
    upsert_pack(PackData(
        id="bayes-pack",
        title="Bayesian Reasoning",
        subtitle="Probability, evidence, updating, and model criticism.",
        level="novice-friendly",
        concepts=[
            PackConcept(id="prior", title="Prior", prerequisites=[], masteryDimension="mastery", exerciseReward="Prior badge earned"),
            PackConcept(id="posterior", title="Posterior", prerequisites=["prior"], masteryDimension="mastery", exerciseReward="Posterior path opened"),
        ],
        onboarding={"headline":"Start with a fast visible win","body":"Read one short orientation, answer one guided question, and leave with your first mastery marker.","checklist":["Read the one-screen topic orientation","Answer one guided exercise","Write one explanation in your own words"]},
        compliance=PackCompliance(sources=2, attributionRequired=True, shareAlikeRequired=True, noncommercialOnly=True, flags=["share-alike","noncommercial","excluded-third-party-content"])
    ), is_published=True)
    print("Seeded database. Demo user: wesley / demo-pass")
