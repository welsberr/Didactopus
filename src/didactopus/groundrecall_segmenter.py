from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from .groundrecall_discovery import DiscoveredArtifact


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FRONTMATTER_DELIM = "---"
ANNOTATION_RE = re.compile(r"\[(claim_id|contradicts|supersedes):([^\]]+)\]", re.IGNORECASE)


@dataclass
class SegmentedObservation:
    artifact_relative_path: str
    role: str
    text: str
    section: str
    line_start: int
    line_end: int
    grounding_status: str
    support_kind: str
    confidence_hint: float
    explicit_claim_key: str = ""
    contradict_keys: list[str] = field(default_factory=list)
    supersede_keys: list[str] = field(default_factory=list)


@dataclass
class SegmentedPage:
    title: str
    headings: list[str] = field(default_factory=list)
    frontmatter: dict[str, str] = field(default_factory=dict)
    observations: list[SegmentedObservation] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)


def _parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], int]:
    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return {}, 0
    data: dict[str, str] = {}
    idx = 1
    while idx < len(lines):
        stripped = lines[idx].strip()
        if stripped == FRONTMATTER_DELIM:
            return data, idx + 1
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            data[key.strip()] = value.strip()
        idx += 1
    return data, 0


def _extract_links(text: str) -> list[str]:
    return re.findall(r"\[\[([^\]]+)\]\]", text)


def _to_concept_id(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return text or "untitled"


def _parse_annotations(text: str) -> tuple[str, str, list[str], list[str]]:
    claim_key = ""
    contradict_keys: list[str] = []
    supersede_keys: list[str] = []
    for kind, raw_value in ANNOTATION_RE.findall(text):
        values = [value.strip() for value in raw_value.split(",") if value.strip()]
        kind_lower = kind.lower()
        if kind_lower == "claim_id" and values:
            claim_key = values[0]
        elif kind_lower == "contradicts":
            contradict_keys.extend(values)
        elif kind_lower == "supersedes":
            supersede_keys.extend(values)
    cleaned = ANNOTATION_RE.sub("", text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned, claim_key, contradict_keys, supersede_keys


def segment_markdown_artifact(artifact: DiscoveredArtifact) -> SegmentedPage:
    text = artifact.path.read_text(encoding="utf-8")
    lines = text.splitlines()
    frontmatter, start_idx = _parse_frontmatter(lines)
    current_section = frontmatter.get("title", Path(artifact.relative_path).stem.replace("-", " ").title())
    title = current_section
    headings: list[str] = []
    observations: list[SegmentedObservation] = []
    concepts: list[str] = []
    links: list[str] = []

    for idx in range(start_idx, len(lines)):
        raw_line = lines[idx]
        stripped = raw_line.strip()
        if not stripped:
            continue
        heading_match = HEADING_RE.match(raw_line)
        if heading_match:
            current_section = heading_match.group(2).strip()
            headings.append(current_section)
            if not title and heading_match.group(1) == "#":
                title = current_section
            concepts.append(_to_concept_id(current_section))
            continue

        role = "summary"
        obs_text = stripped
        if stripped.startswith(("- ", "* ")):
            role = "claim"
            obs_text = stripped[2:].strip()
        elif stripped.lower().startswith(("todo:", "question:", "q:")):
            role = "question"
        elif stripped.lower().startswith(("speculation:", "hypothesis:")):
            role = "speculation"
        elif artifact.artifact_kind == "session_log":
            role = "transcript"

        obs_text, claim_key, contradict_keys, supersede_keys = _parse_annotations(obs_text)

        links.extend(_extract_links(obs_text))
        if role in {"summary", "claim"}:
            concepts.extend(_to_concept_id(link) for link in _extract_links(obs_text))
        observations.append(
            SegmentedObservation(
                artifact_relative_path=artifact.relative_path,
                role=role,
                text=obs_text,
                section=current_section,
                line_start=idx + 1,
                line_end=idx + 1,
                grounding_status="partially_grounded" if artifact.artifact_kind == "compiled_page" else "grounded",
                support_kind="derived_from_page" if artifact.artifact_kind == "compiled_page" else "direct_source",
                confidence_hint=0.55 if role == "speculation" else 0.7 if role == "claim" else 0.6,
                explicit_claim_key=claim_key,
                contradict_keys=contradict_keys,
                supersede_keys=supersede_keys,
            )
        )

    if not headings and title:
        headings.append(title)
    if not concepts and title:
        concepts.append(_to_concept_id(title))
    return SegmentedPage(
        title=title,
        headings=headings,
        frontmatter=frontmatter,
        observations=observations,
        concepts=sorted({c for c in concepts if c}),
        links=sorted({link for link in links if link}),
    )
