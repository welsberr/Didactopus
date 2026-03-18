from __future__ import annotations

import html
import json
from pathlib import Path

from .language_support import ui_text

def _escape(value: object) -> str:
    return html.escape(str(value))


def build_accessible_session_text(session: dict) -> str:
    language = str(session.get("output_language", "en"))
    lines = [
        ui_text("didactopus_learner_session", language),
        "",
        f"{ui_text('learner_goal', language)}: {session.get('goal', '')}",
        f"{ui_text('source_language', language)}: {session.get('source_language', 'en')}",
        f"{ui_text('output_language', language)}: {session.get('output_language', 'en')}",
        "",
        f"{ui_text('study_plan', language)}:",
    ]
    for index, step in enumerate(session.get("study_plan", {}).get("steps", []), start=1):
        lines.extend(
            [
                f"{index}. {step.get('title', '')}",
                f"   {ui_text('status', language)}: {step.get('status', '')}",
                f"   {ui_text('prerequisites', language)}: {', '.join(step.get('prerequisite_titles', []) or ['none explicit'])}",
                f"   {ui_text('supporting_lessons', language)}: {', '.join(step.get('supporting_lessons', []) or ['none listed'])}",
            ]
        )
        for fragment in step.get("source_fragments", [])[:2]:
            lines.append(f"   {ui_text('source_fragment', language)} ({fragment.get('kind', 'fragment')}): {fragment.get('text', '')}")
    lines.extend(
        [
            "",
            f"{ui_text('conversation', language)}:",
        ]
    )
    for turn in session.get("turns", []):
        lines.extend(
            [
                f"{turn.get('label', turn.get('role', 'Turn'))}:",
                str(turn.get("content", "")),
                "",
            ]
        )
    evaluation = session.get("evaluation", {})
    lines.extend(
        [
            f"{ui_text('evaluation_summary', language)}:",
            f"{ui_text('verdict', language)}: {evaluation.get('verdict', '')}",
            f"{ui_text('aggregated_dimensions', language)}: {json.dumps(evaluation.get('aggregated', {}), sort_keys=True)}",
            f"{ui_text('follow_up', language)}: {evaluation.get('follow_up', '')}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_accessible_session_html(session: dict) -> str:
    language = str(session.get("output_language", "en"))
    steps = session.get("study_plan", {}).get("steps", [])
    turns = session.get("turns", [])
    evaluation = session.get("evaluation", {})
    body = [
        "<!doctype html>",
        f'<html lang="{_escape(language)}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_escape(ui_text('didactopus_learner_session', language))}</title>",
        "<style>",
        ":root { color-scheme: light; --bg: #f7f4ed; --panel: #fffdf8; --ink: #1e2b31; --muted: #53656d; --line: #d3c8b7; --accent: #155e63; }",
        "body { margin: 0; font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--ink); line-height: 1.55; }",
        "a { color: var(--accent); }",
        ".skip { position: absolute; left: 12px; top: 12px; background: #fff; padding: 8px 10px; border: 1px solid var(--line); }",
        "main { max-width: 980px; margin: 0 auto; padding: 24px; }",
        "section { background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 20px; margin-bottom: 18px; }",
        "h1, h2, h3 { line-height: 1.2; }",
        "ol, ul { padding-left: 22px; }",
        ".meta { color: var(--muted); }",
        ".turn { border-top: 1px solid var(--line); padding-top: 12px; margin-top: 12px; }",
        ".turn:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }",
        ".fragment { background: #f3efe5; padding: 10px; border-radius: 10px; margin: 8px 0; }",
        ".sr-note { color: var(--muted); font-size: 0.95rem; }",
        "</style>",
        "</head>",
        "<body>",
        f'<a class="skip" href="#session-main">{_escape(ui_text("skip_to_session", language))}</a>',
        '<main id="session-main" aria-label="Didactopus learner session">',
        '<section aria-labelledby="session-title">',
        f'<h1 id="session-title">{_escape(ui_text("didactopus_learner_session", language))}</h1>',
        f'<p class="sr-note">{_escape(ui_text("screen_reader_note", language))}</p>',
        f"<p><strong>{_escape(ui_text('learner_goal', language))}:</strong> {_escape(session.get('goal', ''))}</p>",
        f"<p><strong>{_escape(ui_text('source_language', language))}:</strong> {_escape(session.get('source_language', 'en'))}</p>",
        f"<p><strong>{_escape(ui_text('output_language', language))}:</strong> {_escape(session.get('output_language', 'en'))}</p>",
        "</section>",
        '<section aria-labelledby="study-plan-title">',
        f'<h2 id="study-plan-title">{_escape(ui_text("study_plan", language))}</h2>',
        '<ol>',
    ]
    for step in steps:
        body.append("<li>")
        body.append(f"<h3>{_escape(step.get('title', ''))}</h3>")
        body.append(f"<p><strong>{_escape(ui_text('status', language))}:</strong> {_escape(step.get('status', ''))}</p>")
        body.append(
            f"<p><strong>{_escape(ui_text('prerequisites', language))}:</strong> {_escape(', '.join(step.get('prerequisite_titles', []) or ['none explicit']))}</p>"
        )
        body.append(
            f"<p><strong>{_escape(ui_text('supporting_lessons', language))}:</strong> {_escape(', '.join(step.get('supporting_lessons', []) or ['none listed']))}</p>"
        )
        fragments = step.get("source_fragments", [])[:2]
        if fragments:
            body.append(f"<p><strong>{_escape(ui_text('grounding_fragments', language))}:</strong></p>")
            body.append("<ul>")
            for fragment in fragments:
                body.append(
                    f'<li><div class="fragment"><strong>{_escape(fragment.get("lesson_title", ""))}</strong> '
                    f'({_escape(fragment.get("kind", "fragment"))})<br>{_escape(fragment.get("text", ""))}</div></li>'
                )
            body.append("</ul>")
        body.append("</li>")
    body.extend(
        [
            "</ol>",
            "</section>",
            '<section aria-labelledby="conversation-title">',
            f'<h2 id="conversation-title">{_escape(ui_text("conversation", language))}</h2>',
        ]
    )
    for turn in turns:
        body.append('<article class="turn" aria-label="Conversation turn">')
        body.append(f"<h3>{_escape(turn.get('label', turn.get('role', 'Turn')))}</h3>")
        body.append(f"<p class=\"meta\">Role: {_escape(turn.get('role', ''))}</p>")
        body.append(f"<p>{_escape(turn.get('content', ''))}</p>")
        body.append("</article>")
    body.extend(
        [
            "</section>",
            '<section aria-labelledby="evaluation-title">',
            f'<h2 id="evaluation-title">{_escape(ui_text("evaluation_summary", language))}</h2>',
            f"<p><strong>{_escape(ui_text('verdict', language))}:</strong> {_escape(evaluation.get('verdict', ''))}</p>",
            f"<p><strong>{_escape(ui_text('aggregated_dimensions', language))}:</strong> {_escape(json.dumps(evaluation.get('aggregated', {}), sort_keys=True))}</p>",
            f"<p><strong>{_escape(ui_text('follow_up', language))}:</strong> {_escape(evaluation.get('follow_up', ''))}</p>",
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(body)


def render_accessible_session_outputs(
    session: dict,
    *,
    out_html: str | Path,
    out_text: str | Path,
) -> dict[str, str]:
    out_html = Path(out_html)
    out_text = Path(out_text)
    out_html.write_text(build_accessible_session_html(session), encoding="utf-8")
    out_text.write_text(build_accessible_session_text(session), encoding="utf-8")
    return {"html": str(out_html), "text": str(out_text)}
