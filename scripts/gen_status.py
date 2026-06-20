#!/usr/bin/env python3
"""Generate public/lab-status.json from the lab MDX files.

This mirrors ad-lab-guide/scripts/gen_status.py. The status vocabulary and the
normalize_status() logic are copied verbatim so both guides speak the same
language. The only difference is layout: ad-lab-guide has one status per phase
*file*; this guide has one MDX per *lab* with several `## Phase ...` sections,
each carrying its own `**Status:**` line.

For each src/content/docs/labs/NN-*.mdx it reads:
  - labId / title / labOrder from the frontmatter
  - each `## Phase ...` heading, and the first `**Status:**` line under it

It aggregates phase statuses into a lab-level status (a lab is "done" only when
every phase is done) and writes public/lab-status.json, which Astro copies to the
site root so it is served at https://chweaver.github.io/linux-lab-guide/lab-status.json.

Run BEFORE `astro build` (npm run build does this for you).
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

LABS_DIR = Path("src/content/docs/labs")
OUT = Path("public/lab-status.json")
GUIDE_BASE_URL = "https://chweaver.github.io/linux-lab-guide/"

# Order matters: check longer phrases before single words.
# Copied verbatim from ad-lab-guide so the two guides normalize identically.
STATUS_RULES = [
    ("not started", "planned"),
    ("in progress", "next"),
    ("done", "done"),
    ("next", "next"),
    ("stretch", "stretch"),
]


def normalize_status(raw: str) -> str:
    text = raw.strip().lower().split(".")[0].strip()  # 'done. verified...' -> 'done'
    for key, value in STATUS_RULES:
        if text.startswith(key):
            return value
    return "planned"


def slugify(text: str) -> str:
    """Approximate Starlight's heading-id slug for deep links into a phase."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return slug.strip("-")


def parse_frontmatter(text: str) -> dict:
    """Tiny frontmatter reader (no PyYAML dependency): key: value pairs only."""
    fm = {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return fm
    for line in match.group(1).splitlines():
        kv = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if kv:
            value = kv.group(2).strip().strip('"').strip("'")
            fm[kv.group(1)] = value
    return fm


def aggregate(statuses: list[str]) -> str:
    if not statuses:
        return "planned"
    if all(s == "done" for s in statuses):
        return "done"
    if any(s in ("done", "next") for s in statuses):
        return "next"
    if all(s == "stretch" for s in statuses):
        return "stretch"
    return "planned"


def parse_lab(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    lab_id = fm.get("labId") or md_path.stem
    title = fm.get("title") or md_path.stem
    try:
        order = int(fm.get("labOrder", "0"))
    except ValueError:
        order = 0

    # Body after the frontmatter block.
    body = re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.DOTALL)

    phases = []
    current = None  # {"title", "status_raw"}
    for line in body.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = {"title": heading.group(1).strip(), "status_raw": None}
            # Only `Phase ...` sections are status-bearing; skip Troubleshooting etc.
            if not re.match(r"^Phase\b", current["title"], re.IGNORECASE):
                current = None
            else:
                phases.append(current)
            continue
        if current is not None and current["status_raw"] is None:
            status_match = re.match(r"^\*\*Status:\*\*\s*(.+)", line.strip())
            if status_match:
                current["status_raw"] = status_match.group(1)

    out_phases = []
    for i, ph in enumerate(phases, start=1):
        status = normalize_status(ph["status_raw"]) if ph["status_raw"] else "planned"
        out_phases.append(
            {
                "id": f"{lab_id}-p{i}",
                "labId": lab_id,
                "labTitle": title,
                "title": ph["title"],
                "status": status,
                "anchor": slugify(ph["title"]),
            }
        )

    phase_statuses = [p["status"] for p in out_phases]
    done = sum(1 for s in phase_statuses if s == "done")
    total = len(out_phases)
    return {
        "id": lab_id,
        "title": title,
        "order": order,
        "path": f"labs/{md_path.stem}/",
        "status": aggregate(phase_statuses),
        "pct": round(done / total * 100) if total else 0,
        "phasesTotal": total,
        "phasesDone": done,
        "_phases": out_phases,
    }


def main() -> None:
    labs = []
    for md in sorted(LABS_DIR.glob("*.mdx")):
        labs.append(parse_lab(md))
    labs.sort(key=lambda lab: (lab["order"], lab["id"]))

    phases = []
    for lab in labs:
        phases.extend(lab.pop("_phases"))

    total_phases = len(phases)
    phases_done = sum(1 for p in phases if p["status"] == "done")
    summary = {
        "totalLabs": len(labs),
        "labsComplete": sum(1 for lab in labs if lab["status"] == "done"),
        "totalPhases": total_phases,
        "phasesDone": phases_done,
        "phasesNext": sum(1 for p in phases if p["status"] == "next"),
        "phasesPlanned": sum(1 for p in phases if p["status"] == "planned"),
        "overallPct": round(phases_done / total_phases * 100) if total_phases else 0,
    }

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "guideBaseUrl": GUIDE_BASE_URL,
        "summary": summary,
        "labs": labs,
        "phases": phases,
    }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} with {len(labs)} labs and {total_phases} phases.")


if __name__ == "__main__":
    main()
