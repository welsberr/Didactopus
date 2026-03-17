from pathlib import Path
from didactopus.review_schema import DraftPackData, ConceptReviewEntry, ReviewSession
from didactopus.review_export import export_review_state_json, export_promoted_pack, export_promoted_pack_to_course_repo, export_review_ui_data


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


def test_export_promoted_pack_to_course_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "course").mkdir()
    (repo / "sources.yaml").write_text("sources: []\n", encoding="utf-8")
    (repo / "didactopus-course.yaml").write_text(
        "\n".join(
            [
                "course_id: sample-course",
                "display_name: Sample Course",
                "source_dir: course",
                "source_inventory: sources.yaml",
                "generated_pack_dir: generated/pack",
            ]
        ),
        encoding="utf-8",
    )
    session = ReviewSession(
        reviewer="R",
        draft_pack=DraftPackData(
            pack={"name": "test", "version": "0.1.0-draft"},
            concepts=[ConceptReviewEntry(concept_id="c1", title="C1", status="trusted")],
            attribution={"rights_note": "REVIEW REQUIRED"},
        ),
    )

    target = export_promoted_pack_to_course_repo(session, repo)
    assert target.exists()
    assert (target / "pack.yaml").exists()
