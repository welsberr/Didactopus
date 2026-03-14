from __future__ import annotations

import json
import re
from pathlib import Path

import yaml


def _slug_label(concept_key: str) -> str:
    return concept_key.split("::", 1)[-1].replace("-", " ").title()


def _mean_score(summary: dict[str, float]) -> float:
    if not summary:
        return 0.0
    return sum(summary.values()) / len(summary)


def build_progress_svg(run_summary: dict, capability_profile: dict, width: int = 1400, row_height: int = 74) -> str:
    path = list(run_summary.get("curriculum_path", []))
    mastered = set(capability_profile.get("mastered_concepts", []))
    evaluator_summary = capability_profile.get("evaluator_summary_by_concept", {}) or {}
    artifact_map = {item["concept"]: item for item in capability_profile.get("artifacts", [])}
    height = 210 + max(1, len(path)) * row_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; }",
        ".title { font-size: 32px; font-weight: 700; fill: #123047; }",
        ".subtitle { font-size: 16px; fill: #426173; }",
        ".label { font-size: 16px; font-weight: 600; fill: #163247; }",
        ".meta { font-size: 13px; fill: #4c6473; }",
        ".pill { font-size: 12px; font-weight: 700; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="#f4f1ea"/>',
        '<rect x="34" y="28" width="1332" height="110" rx="24" fill="#fffdf8" stroke="#d8cdb9"/>',
        '<text x="64" y="72" class="title">MIT OCW Information and Entropy: Learner Progress</text>',
        f'<text x="64" y="101" class="subtitle">Target concept: {_slug_label(run_summary["target_concept"])} | '
        f'Mastered {len(mastered)} of {len(path)} guided path concepts | '
        f'Artifacts: {run_summary.get("artifact_count", 0)}</text>',
        '<text x="64" y="124" class="subtitle">Generated from the Didactopus OCW demo run.</text>',
    ]

    line_x = 118
    first_y = 176
    last_y = first_y + (len(path) - 1) * row_height if path else first_y
    parts.append(f'<line x1="{line_x}" y1="{first_y}" x2="{line_x}" y2="{last_y}" stroke="#b2aa99" stroke-width="6" stroke-linecap="round"/>')

    for index, concept_key in enumerate(path):
        y = first_y + index * row_height
        is_mastered = concept_key in mastered
        summary = evaluator_summary.get(concept_key, {})
        mean_score = _mean_score(summary)
        node_fill = "#1d7f5f" if is_mastered else "#c78a15"
        card_fill = "#fffefb" if is_mastered else "#fff8ea"
        card_stroke = "#cfe1d8" if is_mastered else "#e4d1a7"
        artifact = artifact_map.get(concept_key)
        artifact_label = artifact["artifact_name"] if artifact else "no artifact"

        parts.append(f'<circle cx="{line_x}" cy="{y}" r="17" fill="{node_fill}" stroke="#ffffff" stroke-width="4"/>')
        parts.append(f'<rect x="150" y="{y - 28}" width="1180" height="56" rx="18" fill="{card_fill}" stroke="{card_stroke}"/>')
        parts.append(f'<text x="178" y="{y - 4}" class="label">{index + 1}. {_slug_label(concept_key)}</text>')
        parts.append(
            f'<text x="178" y="{y + 18}" class="meta">{concept_key} | mean evaluator score {mean_score:.2f} | artifact {artifact_label}</text>'
        )
        pill_fill = "#d8efe6" if is_mastered else "#f6e2b7"
        pill_text = "#1d5d47" if is_mastered else "#8a5a00"
        pill_label = "MASTERED" if is_mastered else "IN PROGRESS"
        parts.append(f'<rect x="1180" y="{y - 18}" width="120" height="28" rx="14" fill="{pill_fill}"/>')
        parts.append(f'<text x="1240" y="{y + 1}" text-anchor="middle" class="pill" fill="{pill_text}">{pill_label}</text>')
    parts.append("</svg>")
    return "".join(parts)


def build_progress_html(svg: str) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"en\">",
            "<meta charset=\"utf-8\">",
            "<title>MIT OCW Information and Entropy Learner Progress</title>",
            "<body style=\"margin:0;background:#ece7dd;display:flex;justify-content:center;padding:24px;\">",
            svg,
            "</body>",
            "</html>",
        ]
    )


def _extract_lesson_name(description: str) -> str | None:
    match = re.search(r"lesson '([^']+)'", description)
    return match.group(1) if match else None


def build_full_concept_map_svg(run_summary: dict, capability_profile: dict, concepts_data: dict, width: int = 1760) -> str:
    path = list(run_summary.get("curriculum_path", []))
    mastered = set(capability_profile.get("mastered_concepts", []))
    evaluator_summary = capability_profile.get("evaluator_summary_by_concept", {}) or {}
    concepts = concepts_data.get("concepts", []) or []
    pack_name = run_summary["target_concept"].split("::", 1)[0]
    title_by_key = {key: _slug_label(key) for key in path}
    key_by_title = {value: key for key, value in title_by_key.items()}
    grouped: dict[str, list[dict]] = {key: [] for key in path}

    for concept in concepts:
        concept_key = f"{pack_name}::{concept['id']}"
        if concept_key in grouped:
            continue
        lesson_name = _extract_lesson_name(str(concept.get("description", "")))
        anchor = None
        if concept.get("prerequisites"):
            anchor = f"{pack_name}::{concept['prerequisites'][0]}"
        elif lesson_name and lesson_name in key_by_title:
            anchor = key_by_title[lesson_name]
        else:
            anchor = path[0] if path else concept_key
        if anchor not in grouped:
            grouped[anchor] = []
        grouped[anchor].append(concept)

    row_height = 124
    top = 210
    height = max(1200, top + max(1, len(path)) * row_height + 120)
    center_x = width // 2
    left_x = 280
    right_x = width - 280
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text { font-family: Arial, sans-serif; }",
        ".title { font-size: 34px; font-weight: 700; fill: #123047; }",
        ".subtitle { font-size: 16px; fill: #496476; }",
        ".core { font-size: 17px; font-weight: 700; fill: #173042; }",
        ".meta { font-size: 12px; fill: #516877; }",
        ".small { font-size: 11px; fill: #6e7f89; }",
        "</style>",
        '<rect x="0" y="0" width="100%" height="100%" fill="#f2efe8"/>',
        '<rect x="32" y="28" width="1696" height="120" rx="24" fill="#fffdf8" stroke="#d7cfbf"/>',
        '<text x="58" y="72" class="title">MIT OCW Information and Entropy: Full Concept Map</text>',
        '<text x="58" y="100" class="subtitle">Center column = guided mastery path. Side nodes = extractor spillover and auxiliary concepts grouped by lesson anchor.</text>',
        '<text x="58" y="123" class="subtitle">Green = mastered path concept, blue = structured but unmastered, sand = noisy side concept.</text>',
        f'<line x1="{center_x}" y1="{top}" x2="{center_x}" y2="{top + (len(path) - 1) * row_height if path else top}" stroke="#b8b09f" stroke-width="8" stroke-linecap="round"/>',
    ]

    for index, concept_key in enumerate(path):
        y = top + index * row_height
        title = _slug_label(concept_key)
        summary = evaluator_summary.get(concept_key, {})
        mean_score = _mean_score(summary)
        is_mastered = concept_key in mastered
        node_fill = "#237a61" if is_mastered else "#4f86c6"
        card_fill = "#f5fbf8" if is_mastered else "#eef4fb"
        card_stroke = "#b9d8cc" if is_mastered else "#c8d7eb"

        parts.append(f'<circle cx="{center_x}" cy="{y}" r="20" fill="{node_fill}" stroke="#ffffff" stroke-width="4"/>')
        parts.append(f'<rect x="{center_x - 180}" y="{y - 31}" width="360" height="62" rx="20" fill="{card_fill}" stroke="{card_stroke}"/>')
        parts.append(f'<text x="{center_x}" y="{y - 6}" text-anchor="middle" class="core">{index + 1}. {title}</text>')
        parts.append(f'<text x="{center_x}" y="{y + 16}" text-anchor="middle" class="meta">{concept_key} | mean score {mean_score:.2f}</text>')

        satellites = sorted(grouped.get(concept_key, []), key=lambda item: item.get("title", item.get("id", "")))
        left_items = satellites[::2][:5]
        right_items = satellites[1::2][:5]
        for side, items in ((-1, left_items), (1, right_items)):
            base_x = left_x if side < 0 else right_x
            for sat_index, item in enumerate(items):
                sat_y = y - 34 + sat_index * 17
                sat_width = 250
                rect_x = base_x - sat_width // 2
                parts.append(f'<line x1="{center_x + side * 24}" y1="{y}" x2="{base_x - side * 130}" y2="{sat_y}" stroke="#d1c6ae" stroke-width="2"/>')
                parts.append(f'<rect x="{rect_x}" y="{sat_y - 12}" width="{sat_width}" height="24" rx="12" fill="#fbf3de" stroke="#e3cf99"/>')
                parts.append(
                    f'<text x="{base_x}" y="{sat_y + 4}" text-anchor="middle" class="small">{item.get("title", item.get("id", ""))}</text>'
                )
        hidden_count = max(0, len(satellites) - 10)
        if hidden_count:
            parts.append(f'<text x="{right_x + 170}" y="{y + 42}" class="small">+{hidden_count} more side concepts</text>')

    parts.append("</svg>")
    return "".join(parts)


def render_ocw_progress_visualization(run_dir: str | Path, out_svg: str | Path | None = None, out_html: str | Path | None = None) -> dict[str, str]:
    run_dir = Path(run_dir)
    run_summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    capability_profile = json.loads((run_dir / "capability_profile.json").read_text(encoding="utf-8"))

    svg = build_progress_svg(run_summary, capability_profile)
    out_svg = Path(out_svg) if out_svg is not None else run_dir / "learner_progress.svg"
    out_html = Path(out_html) if out_html is not None else run_dir / "learner_progress.html"
    out_svg.write_text(svg, encoding="utf-8")
    out_html.write_text(build_progress_html(svg), encoding="utf-8")
    return {"svg": str(out_svg), "html": str(out_html)}


def render_ocw_full_concept_map(
    run_dir: str | Path,
    pack_dir: str | Path,
    out_svg: str | Path | None = None,
    out_html: str | Path | None = None,
) -> dict[str, str]:
    run_dir = Path(run_dir)
    pack_dir = Path(pack_dir)
    run_summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    capability_profile = json.loads((run_dir / "capability_profile.json").read_text(encoding="utf-8"))
    concepts_data = yaml.safe_load((pack_dir / "concepts.yaml").read_text(encoding="utf-8")) or {}
    svg = build_full_concept_map_svg(run_summary, capability_profile, concepts_data)
    out_svg = Path(out_svg) if out_svg is not None else run_dir / "learner_progress_full_map.svg"
    out_html = Path(out_html) if out_html is not None else run_dir / "learner_progress_full_map.html"
    out_svg.write_text(svg, encoding="utf-8")
    out_html.write_text(build_progress_html(svg), encoding="utf-8")
    return {"svg": str(out_svg), "html": str(out_html)}


def main() -> None:
    import argparse

    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Render learner progress visualization for the OCW Information and Entropy demo.")
    parser.add_argument(
        "--run-dir",
        default=str(root / "examples" / "ocw-information-entropy-run"),
    )
    parser.add_argument(
        "--pack-dir",
        default=str(root / "domain-packs" / "mit-ocw-information-entropy"),
    )
    parser.add_argument("--out-svg", default=None)
    parser.add_argument("--out-html", default=None)
    parser.add_argument("--full-map", action="store_true")
    args = parser.parse_args()
    if args.full_map:
        outputs = render_ocw_full_concept_map(args.run_dir, args.pack_dir, args.out_svg, args.out_html)
    else:
        outputs = render_ocw_progress_visualization(args.run_dir, args.out_svg, args.out_html)
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
