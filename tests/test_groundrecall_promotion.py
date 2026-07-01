from __future__ import annotations

import json
from pathlib import Path

from didactopus.groundrecall.ingest import run_groundrecall_import
from didactopus.groundrecall.promotion import promote_import_to_store
from didactopus.groundrecall.store import GroundRecallStore


def test_groundrecall_promotion_writes_canonical_objects(tmp_path: Path) -> None:
    root = tmp_path / "llmwiki"
    (root / "wiki").mkdir(parents=True)
    (root / "wiki" / "channel-capacity.md").write_text(
        "# Channel Capacity\n\n"
        "- Reliable rate upper bound for a noisy channel.\n\n"
        "See also [[Shannon Entropy]].\n",
        encoding="utf-8",
    )

    result = run_groundrecall_import(root, mode="quick", import_id="promote-test")
    review_path = result.out_dir / "review_session.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    for concept in review_payload["draft_pack"]["concepts"]:
        concept["status"] = "trusted"
    review_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    store_dir = tmp_path / "groundrecall-store"
    payload = promote_import_to_store(result.out_dir, store_dir, reviewer="R")

    store = GroundRecallStore(store_dir)
    concepts = store.list_concepts()
    claims = store.list_claims()
    relations = store.list_relations()
    promotions = store.list_promotions()
    snapshots = store.list_snapshots()

    assert payload["promoted_concept_count"] >= 1
    assert payload["promoted_claim_count"] >= 1
    assert len(concepts) >= 2
    assert any(item.current_status == "promoted" for item in concepts)
    assert any(item.current_status == "promoted" for item in claims)
    assert len(relations) >= 1
    assert len(promotions) == 1
    assert promotions[0].reviewer == "R"
    assert len(snapshots) == 1
    assert snapshots[0].metadata["source_import_id"] == "promote-test"


def test_groundrecall_promotion_respects_rejected_review_status(tmp_path: Path) -> None:
    root = tmp_path / "llmwiki"
    (root / "wiki").mkdir(parents=True)
    (root / "wiki" / "solo.md").write_text(
        "# Solo Concept\n\n- A solitary claim.\n",
        encoding="utf-8",
    )

    result = run_groundrecall_import(root, mode="quick", import_id="reject-test")
    review_path = result.out_dir / "review_session.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    review_payload["draft_pack"]["concepts"][0]["status"] = "rejected"
    review_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    store_dir = tmp_path / "groundrecall-store"
    promote_import_to_store(result.out_dir, store_dir, reviewer="R")

    store = GroundRecallStore(store_dir)
    assert store.list_concepts()[0].current_status == "rejected"
    assert store.list_claims()[0].current_status == "rejected"


def test_groundrecall_promotion_preserves_contradiction_and_supersession_links(tmp_path: Path) -> None:
    root = tmp_path / "llmwiki"
    (root / "wiki").mkdir(parents=True)
    (root / "wiki" / "notes.md").write_text(
        "# Notes\n\n"
        "- [claim_id: base] Channel capacity bounds reliable communication rate.\n"
        "- [claim_id: revised] [supersedes: base] Channel capacity bounds reliable communication rate for a specified channel model.\n"
        "- [claim_id: dissent] [contradicts: revised] Channel capacity has no stable interpretation.\n",
        encoding="utf-8",
    )

    result = run_groundrecall_import(root, mode="quick", import_id="graph-test")
    review_path = result.out_dir / "review_session.json"
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    for concept in review_payload["draft_pack"]["concepts"]:
        concept["status"] = "trusted"
    review_path.write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    store_dir = tmp_path / "groundrecall-store"
    promote_import_to_store(result.out_dir, store_dir, reviewer="R")

    store = GroundRecallStore(store_dir)
    claims = {item.claim_id: item for item in store.list_claims()}
    assert claims["clm_revised"].supersedes_claim_ids == ["clm_base"]
    assert claims["clm_dissent"].contradicts_claim_ids == ["clm_revised"]
