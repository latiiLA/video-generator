"""Export Assignment 1 REPORT.md content to a submission Word document."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Lata_Amenu_Heritage_Short_Assignment1_Report.docx"


def main() -> None:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    def heading(text: str, level: int = 1) -> None:
        doc.add_heading(text, level=level)

    def para(text: str, *, bold: bool = False) -> None:
        p = doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold

    def bullets(items: list[str]) -> None:
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    def add_table(headers: list[str], rows: list[list[str]]) -> None:
        table = doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = "Table Grid"
        for i, header in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.text = header
            for run in cell.paragraphs[0].runs:
                run.bold = True
        for r_i, row in enumerate(rows):
            for c_i, val in enumerate(row):
                table.rows[r_i + 1].cells[c_i].text = val
        doc.add_paragraph()

    doc.add_heading("Assignment 1 Report — The Heritage Short", 0)
    meta = doc.add_paragraph()
    for line in [
        "Film title: The Summer I Discovered Another World",
        "Author: Lata Amenu",
        "Programme: 10 Academy · B2W0 Challenge",
        "On-film / UI credit: Made by Lata Amenu",
        "Repository: https://github.com/latiiLA/video-generator",
        "Date: 26 November 2026",
    ]:
        meta.add_run(line + "\n")

    para(
        "This report accompanies the public codebase. Evidence lives in DESIGN.md, "
        "ARCHITECTURE.md, EXPERIMENTS.md, FAILURES.md, COSTS.md, ETHICS.md, "
        "CONTRIBUTIONS.md, and runs.jsonl."
    )

    heading("1. What I set out to make, and for whom")
    para(
        "I set out to make a 60–90 second heritage short about one Grade Seven summer "
        "at my grandfather’s place in rural Wallaga: endless greenery, summer rain, "
        "work on the land, firelight in a gojo, potatoes cooking, fresh milk, and the "
        "feeling that ordinary days become memory."
    )
    para(
        "Audience. Relatives who already know that countryside world, and friends who "
        "grew up only in city life—people watching primarily on a phone (9:16), with a "
        "horizontal 16:9 cut for wider sharing."
    )
    para(
        "Intent. Feel how precious that “simple visit” was, and understand that the "
        "most beautiful journeys can be the ones that take us back to where we first "
        "learned to see."
    )
    para(
        "Contract. The film is driven by a validated storyboard.json (active creative "
        "source: storyboards/wallaga_summer.json). A first draft that used public "
        "history (Kumsa Moroda) was replaced so the film would be for family, not a lecture."
    )
    para(
        "Shipped language path. English male narration (stock TTS, not a relative’s "
        "voice) with Amharic burned-in captions, dual-aspect export, ducked score, and "
        "an AI-labelled end card."
    )

    heading("2. What I learned from the audience")
    heading("Design pivot before formal picture spend", 2)
    para(
        "Early feedback on the public-history draft was that it felt like a lecture. I "
        "replaced it with the personal Wallaga chronology (nine shots, each with an "
        "explicit reason). If the first viewer cannot feel who it is for, pipeline "
        "polish will not save the film."
    )

    heading("User test 1 — radio cut (narration-first)", 2)
    bullets(
        [
            "Prototype: narration-first / radio path (make radio and early VO assembly) before committing image quota.",
            "Participants (≥3): three listeners drawn from classmates and family (countryside-familiar and city-only).",
            "What they said: the opening “I thought it was only a visit” lands; gojo night and fresh milk are the emotional centre; Afaan Oromo TTS was hard to trust in our free-tier path; English VO was clearer for mixed listeners; Amharic on-screen text helps relatives.",
            "What I changed: locked the nine-beat personal chronology; English narration spine; Amharic burned-in captions; kept longer beats on gojo and milk.",
        ]
    )

    heading("User test 2 — near-final cut", 2)
    bullets(
        [
            "Prototype: outputs/film/final_9x16.mp4 (and matching 16:9).",
            "Participants (≥3): three viewers (phone-first vertical; one desktop horizontal).",
            "What they said: vertical fits phone audience; faces must read as Horn of Africa / Ethiopian; gentle Ken Burns is acceptable if voice and captions carry the story; AI labelling is fine; author credit “Made by Lata Amenu” matters on the showcase.",
            "What I changed: stronger Ethiopian facial descriptors in style_block and prompts; Ken Burns as default motion floor; dual native aspects; Film tab Drive embeds with author credit in the UI.",
        ]
    )

    heading("3. Hardest problem and how I solved it")
    para(
        "The hardest problem was keeping a reproducible multi-model pipeline alive on "
        "free tiers while APIs, model IDs, and hosts moved under us—and then making the "
        "same pipeline reachable from a deployed web UI."
    )
    add_table(
        ["Failure class", "What broke", "Fix"],
        [
            ["Model IDs", "Gemini 404 / 503 on free tier", "Fallback chain in pipeline/config.py (Flash-Lite first)"],
            ["Image API", "Cloudflare FLUX rejecting seed", "Drop seed from request; keep seed for cache keys only"],
            ["TTS", "API shape changes + 429 quota", "Interactions TTS, then Edge TTS male EN fallback"],
            ["Local tooling", "FFmpeg missing on Windows PATH", "imageio-ffmpeg via config.ffmpeg_exe()"],
            ["Motion / music GPU", "No local Wan / ACE-Step", "Ken Burns + procedural bed; Kaggle drop-in folders"],
            ["Hosting", "Railway start / PORT pain", "Render Docker worker (Dockerfile, render.yaml)"],
            ["Web errors", "FastAPI detail as [object Object]", "formatError stringification in Next.js jobs API"],
            [
                "Schema drift",
                "Gemini end_card title/subtitle; demo shots < minItems",
                "normalize_storyboard in validate_storyboard; 6-shot Quick Test board",
            ],
        ],
    )
    para("Evidence: FAILURES.md, runs.jsonl, pipeline/common.py, web/lib/demoStoryboard.ts.")

    heading("4. Suggested practice that beat my instinct")
    para("Radio cut / narration-first.", bold=True)
    para(
        "My instinct was to generate pictures early so the project would look like a "
        "film. The brief’s radio-cut practice beat that instinct. Timing the voice "
        "first (make radio) and treating storyboard.json as the only contract caught "
        "language, pacing, and story-subject problems before spending FLUX quota. Later "
        "stages only read the storyboard and write their own outputs, with content-hash "
        "caching so one changed line does not rebuild the world."
    )

    heading("5. Suggested practice that did not beat my instinct")
    para("Own-language narration as the default first ship.", bold=True)
    para(
        "Instinct and the brief both push heritage language (Afaan Oromo). I tried "
        "Oromo lines early; the path hung or became unusable under our free-tier calls. "
        "For the deadline film I shipped English male VO + Amharic captions, and kept "
        "the Oromo attempt as an honest ceiling/failure experiment rather than silently "
        "pretending the first film was Oromo-narrated."
    )

    heading("6. Ceiling work")
    bullets(
        [
            "Family / showcase web app (web/): Film tab (Drive 16:9 + 9:16), Generate, Quick Test, live stage progress — not only a CLI.",
            "Deploy split: Vercel UI + Render Docker worker (Vercel cannot run FFmpeg).",
            "Dual native aspects: true 16:9 and 9:16 assemble paths.",
            "Language path: English VO + Amharic captions; Oromo TTS measured as failure.",
            "Deploy hardening: storyboard normalization, embedded Quick Test board, worker demo=true path.",
        ]
    )
    para("Authorship and file map: CONTRIBUTIONS.md.")

    heading("7. What I would build next")
    bullets(
        [
            "Batch real Wan 2.2 clips and ACE-Step music candidates from Kaggle, then re-assemble.",
            "Retry Afaan Oromo with shorter lines and a native listener before picture spend.",
            "Blind preference test (Ken Burns vs Wan) with five viewers; append to EXPERIMENTS.md.",
            "If a frontier lane opens, compare one shot blind and record cost/latency in COSTS.md.",
        ]
    )

    heading("8. Evidence map")
    add_table(
        ["Claim", "Where in the repo"],
        [
            ["Audience, intent, chronology, user tests", "DESIGN.md"],
            ["Stages, cache, web/worker topology", "ARCHITECTURE.md"],
            ["≥10 experiments with results", "EXPERIMENTS.md"],
            ["Failures and fixes", "FAILURES.md"],
            ["Measured latency / free-tier path", "COSTS.md, runs.jsonl"],
            ["Consent, licences, AI labelling", "ETHICS.md"],
            ["Authorship / what I built", "CONTRIBUTIONS.md"],
            ["One command", "README.md, Makefile, scripts/run_film.ps1"],
            ["Storyboard contract + schema", "storyboard.json, schema/, storyboards/wallaga_summer.json"],
            ["Pipeline implementation", "pipeline/"],
            ["Web + worker", "web/, pipeline/worker.py, Dockerfile, render.yaml"],
            ["Showcase film links", "web/lib/film.ts"],
        ],
    )

    heading("9. Ethics summary")
    bullets(
        [
            "Stylized AI imagery; no photoreal clones of named relatives; no voice clone.",
            "End card / platform labelling: Made with AI; author credit Made by Lata Amenu.",
            "Private identifiers kept out of free endpoints that may train on inputs.",
        ]
    )
    para("Full table: ETHICS.md.")

    heading("10. How to reproduce")
    para(
        "Clone the repo. Use Python 3.11+, create a venv, pip install -r requirements.txt, "
        "copy .env.example to .env and add GEMINI_API_KEY plus Cloudflare keys. Run: "
        "powershell -File scripts/run_film.ps1 → outputs/film/final_9x16.mp4 and "
        "final_16x9.mp4. Web locally: make web-dev and make worker (see README.md)."
    )

    para("End of Assignment 1 report — Lata Amenu.", bold=True)

    doc.save(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
