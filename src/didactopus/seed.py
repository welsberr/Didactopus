from __future__ import annotations
from sqlalchemy import select
from .db import Base, engine, SessionLocal
from .orm import UserORM
from .auth import hash_password
from .repository import upsert_pack, create_learner
from .models import PackData, PackConcept, GraphPosition, CrossPackLink

def main():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.execute(select(UserORM).where(UserORM.username == "wesley")).scalar_one_or_none() is None:
            db.add(UserORM(username="wesley", password_hash=hash_password("demo-pass"), role="admin", is_active=True))
        db.commit()
    create_learner(1, "wesley-learner", "Wesley learner")
    upsert_pack(
        PackData(
            id="wesley-private-pack",
            title="Wesley Private Pack",
            subtitle="Personal pack example.",
            level="novice-friendly",
            concepts=[
                PackConcept(id="intro", title="Intro", prerequisites=[], position=GraphPosition(x=150, y=120)),
                PackConcept(id="second", title="Second concept", prerequisites=["intro"], position=GraphPosition(x=420, y=120)),
                PackConcept(id="third", title="Third concept", prerequisites=["second"], position=GraphPosition(x=700, y=120), cross_pack_links=[CrossPackLink(source_concept_id="third", target_pack_id="advanced-pack", target_concept_id="adv-1", relationship="next_pack")]),
                PackConcept(id="branch", title="Branch concept", prerequisites=["intro"], position=GraphPosition(x=420, y=320)),
            ],
            onboarding={"headline":"Start privately"},
            compliance={}
        ),
        submitted_by_user_id=1,
        policy_lane="personal",
        is_published=True,
    )
