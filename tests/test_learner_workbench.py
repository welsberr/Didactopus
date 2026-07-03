import json
import shutil
from pathlib import Path

from didactopus import learner_workbench as learner_workbench_module


class _FakeProvider:
    def __init__(self, _config) -> None:
        pass

    def generate(
        self,
        prompt: str,
        *,
        role: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        return type(
            "Response",
            (),
            {
                "text": f"{role}: {' | '.join(prompt.splitlines()[:30])}",
                "provider": "fake",
                "model_name": "fake-model",
            },
        )()


def test_build_pack_workbench_session_uses_evidence_trail_pack(monkeypatch) -> None:
    monkeypatch.setattr(learner_workbench_module, "ModelProvider", _FakeProvider)

    payload = learner_workbench_module.build_pack_workbench_session(
        pack_id="evidence-trail",
        concept_id="question-framing",
        learner_goal="Understand how to compare evidence.",
        question="Which question should guide the study step?",
        observation="The pack starts with question framing.",
        interpretation="Question framing organizes the next evidence move.",
        uncertainty="I do not yet know which source will best test the interpretation.",
        revision_trigger="A stronger source trail could change the current framing.",
    )

    assert payload["pack_id"] == "evidence-trail"
    assert payload["concept_id"] == "question-framing"
    assert payload["next_concept_id"] == "observation-vs-interpretation"
    assert payload["mentor"]["provider"] == "fake"
    assert payload["feedback"]["strengths"]
    assert payload["feedback"]["gaps"] == []


def test_build_pack_workbench_session_includes_groundrecall_context(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(learner_workbench_module, "ModelProvider", _FakeProvider)
    source_pack = learner_workbench_module.DOMAIN_PACKS / "evidence-trail"
    copied_root = tmp_path / "domain-packs"
    copied_pack = copied_root / "evidence-trail"
    shutil.copytree(source_pack, copied_pack)
    (copied_pack / "groundrecall_query_bundle.json").write_text(
        json.dumps(
            {
                "bundle_kind": "groundrecall_query_bundle",
                "concept": {"concept_id": "concept::question-framing", "title": "Question Framing"},
                "source_role_summary": {"overview": 1, "argumentation": 1},
                "key_distinctions": [
                    {
                        "claim_id": "clm_001",
                        "distinction_type": "non_implication",
                        "cue": "does not imply",
                        "text": "A guiding question does not imply a settled interpretation.",
                    }
                ],
                "review_candidates": [
                    {
                        "candidate_id": "concept::question-framing",
                        "finding_codes": ["bridge_concept"],
                        "rationale": "Question Framing | lane=conflict_resolution | priority=12 | graph=bridge_concept",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(learner_workbench_module, "DOMAIN_PACKS", copied_root)

    payload = learner_workbench_module.build_pack_workbench_session(
        pack_id="evidence-trail",
        concept_id="question-framing",
        learner_goal="Understand how to compare evidence.",
        question="Which question should guide the study step?",
        observation="The pack starts with question framing.",
        interpretation="Question framing organizes the next evidence move.",
        uncertainty="I do not yet know which source will best test the interpretation.",
        revision_trigger="A stronger source trail could change the current framing.",
    )

    assert payload["groundrecall"]["review_candidate_count"] == 1
    assert payload["groundrecall"]["graph_codes"] == ["bridge_concept"]
    assert payload["groundrecall"]["source_role_summary"]["overview"] == 1
    assert payload["groundrecall"]["key_distinctions"][0]["distinction_type"] == "non_implication"
    assert "GroundRecall context:" in payload["mentor"]["text"]
    assert "Source roles:" in payload["mentor"]["text"]
    assert "Distinction" in payload["mentor"]["text"]


def test_build_pack_workbench_session_includes_groundrecall_interchange_quality(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(learner_workbench_module, "ModelProvider", _FakeProvider)
    source_pack = learner_workbench_module.DOMAIN_PACKS / "evidence-trail"
    copied_root = tmp_path / "domain-packs"
    copied_pack = copied_root / "evidence-trail"
    shutil.copytree(source_pack, copied_pack)
    (copied_pack / "graph_interchange.json").write_text(
        json.dumps(
            {
                "bundle_kind": "groundrecall_graph_interchange",
                "schema_version": "groundrecall.graph_interchange.v1",
                "snapshot_id": "snap-test",
                "created_at": "2026-07-01T00:00:00Z",
                "nodes": [
                    {
                        "node_id": "concept::question-framing",
                        "node_kind": "concept",
                        "title": "Question Framing",
                        "description": "Choose a study question.",
                        "status": "promoted",
                    }
                ],
                "edges": [],
                "claims": [],
                "observations": [],
                "diagnostics": {
                    "quality_summary": {
                        "inferred_relation_count": 2,
                        "weakly_grounded_relation_count": 1,
                        "unsupported_claim_count": 0,
                    }
                },
                "consumer_notes": [],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(learner_workbench_module, "DOMAIN_PACKS", copied_root)

    payload = learner_workbench_module.build_pack_workbench_session(
        pack_id="evidence-trail",
        concept_id="question-framing",
        learner_goal="Understand how to compare evidence.",
        question="Which question should guide the study step?",
        observation="The pack starts with question framing.",
        interpretation="Question framing organizes the next evidence move.",
        uncertainty="I do not yet know which source will best test the interpretation.",
        revision_trigger="A stronger source trail could change the current framing.",
    )

    assert payload["groundrecall"]["graph_interchange_included"] is True
    assert payload["groundrecall"]["graph_node_count"] == 1
    assert payload["groundrecall"]["graph_quality_summary"]["inferred_relation_count"] == 2
    assert "Graph interchange: nodes=1, edges=0" in payload["mentor"]["text"]
    assert "Graph quality signals:" in payload["mentor"]["text"]
