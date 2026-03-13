from pathlib import Path
from didactopus.review_schema import DraftPackData, ConceptReviewEntry, ReviewSession
from didactopus.review_export import export_review_state_json, export_promoted_pack, export_review_ui_data


def test_exports(tmp_path: Path) -> None:
    session = ReviewSession(
        reviewer="R",
        draft_pack=DraftPackData(
            pack={"name": "test", "version": "0.1.0-draft"},
            concepts=[ConceptReviewEntry(concept_id="c1", title="C1", status="trusted")],
            attribution={"rights_note": "REVIEW REQUIRED"},
        ),
    )
    export_review_state_json(session, tmp_path / "review_session.json")
    export_review_ui_data(session, tmp_path)
    export_promoted_pack(session, tmp_path / "promoted")
    assert (tmp_path / "review_session.json").exists()
    assert (tmp_path / "review_data.json").exists()
    assert (tmp_path / "promoted" / "pack.yaml").exists()
