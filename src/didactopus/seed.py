from __future__ import annotations
import json
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .orm import UserORM, PackORM
from .auth import hash_password

def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.execute(select(UserORM).where(UserORM.username == "wesley")).scalar_one_or_none() is None:
            db.add(UserORM(username="wesley", password_hash=hash_password("demo-pass"), role="admin", is_active=True))
        if db.execute(select(UserORM).where(UserORM.username == "reviewer")).scalar_one_or_none() is None:
            db.add(UserORM(username="reviewer", password_hash=hash_password("demo-pass"), role="reviewer", is_active=True))
        if db.get(PackORM, "biology-pack") is None:
            db.add(PackORM(
                id="biology-pack",
                owner_user_id=1,
                policy_lane="personal",
                title="Biology Pack",
                subtitle="Core biology concepts",
                level="novice-friendly",
                is_published=True,
                data_json=json.dumps({
                    "id": "biology-pack",
                    "title": "Biology Pack",
                    "concepts": [
                        {"id": "selection", "title": "Natural Selection", "prerequisites": ["variation"]},
                        {"id": "variation", "title": "Variation", "prerequisites": []},
                        {"id": "drift", "title": "Genetic Drift", "prerequisites": ["variation"]}
                    ]
                })
            ))
        if db.get(PackORM, "math-pack") is None:
            db.add(PackORM(
                id="math-pack",
                owner_user_id=1,
                policy_lane="personal",
                title="Math Pack",
                subtitle="Core math concepts",
                level="novice-friendly",
                is_published=True,
                data_json=json.dumps({
                    "id": "math-pack",
                    "title": "Math Pack",
                    "concepts": [
                        {"id": "random_walk", "title": "Random Walk", "prerequisites": ["variation"]},
                        {"id": "variation", "title": "Variation in Models", "prerequisites": []},
                        {"id": "optimization", "title": "Optimization", "prerequisites": []}
                    ]
                })
            ))
        db.commit()
