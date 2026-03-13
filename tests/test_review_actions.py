from didactopus.review_schema import DraftPackData, ConceptReviewEntry, ReviewSession, ReviewAction
from didactopus.review_actions import apply_action


def test_apply_status_action() -> None:
    session = ReviewSession(
        reviewer="R",
        draft_pack=DraftPackData(
            concepts=[ConceptReviewEntry(concept_id="c1", title="C1")]
        ),
    )
    apply_action(session, "R", ReviewAction(action_type="set_status", target="c1", payload={"status": "trusted"}))
    assert session.draft_pack.concepts[0].status == "trusted"
    assert len(session.ledger) == 1
