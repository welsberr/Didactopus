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
    upsert_pack(
        PackData(
            id="wesley-private-pack",
            title="Wesley Private Pack",
            subtitle="Personal pack example.",
            level="novice-friendly",
            concepts=[PackConcept(id="intro", title="Intro", prerequisites=[], masteryDimension="mastery", exerciseReward="Intro marker")],
            onboarding={"headline":"Start privately","body":"Personal pack lane.","checklist":["Create pack","Use pack"]},
            compliance=PackCompliance()
        ),
        submitted_by_user_id=1,
        policy_lane="personal",
        is_published=True,
        change_summary="Initial personal pack"
    )
