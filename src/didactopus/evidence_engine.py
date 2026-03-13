from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ConceptEvidenceSummary:
    concept_key: str
    weak_dimensions: list[str] = field(default_factory=list)
    mastered: bool = False


@dataclass
class EvidenceState:
    summary_by_concept: dict[str, ConceptEvidenceSummary] = field(default_factory=dict)
    resurfaced_concepts: set[str] = field(default_factory=set)
