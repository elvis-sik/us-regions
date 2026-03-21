#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DIVISION_CSV = REPO_ROOT / "data/raw/us_divisions_notes_seed.csv"
STATE_REFERENCE_CSV = REPO_ROOT / "data/raw/us_state_border_reference.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def split_pipes(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def render_segment(label: str, items: list[str]) -> str:
    if not items:
        return ""
    return f"{label} " + ", ".join(items)


def build_state_lookup() -> dict[str, dict[str, str]]:
    rows = read_rows(STATE_REFERENCE_CSV)
    return {(row.get("state_code") or "").strip().upper(): row for row in rows}


def build_summary_line(state_row: dict[str, str], state_lookup: dict[str, dict[str, str]]) -> str:
    neighbor_codes = split_pipes(state_row.get("neighbor_state_codes") or "")
    neighbor_names = [
        (state_lookup[code].get("state_name") or code).strip()
        for code in neighbor_codes
        if code in state_lookup
    ]
    countries = split_pipes(state_row.get("neighbor_countries") or "")
    oceans = split_pipes(state_row.get("neighbor_oceans") or "")

    segments = [
        render_segment("states:", neighbor_names),
        render_segment("countries:", countries),
        render_segment("oceans:", oceans),
    ]
    segments = [segment for segment in segments if segment]
    return f"{state_row['state_name']}: " + "; ".join(segments)


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    state_lookup = build_state_lookup()
    division_rows = read_rows(DIVISION_CSV)
    if not division_rows:
        return 0

    for row in division_rows:
        member_codes = split_pipes(row.get("member_state_codes") or "")
        summary_lines = [
            build_summary_line(state_lookup[code], state_lookup)
            for code in member_codes
            if code in state_lookup
        ]
        row["state_border_summary"] = "\n".join(summary_lines)

    write_rows(DIVISION_CSV, division_rows, list(division_rows[0].keys()))
    print(f"updated {DIVISION_CSV.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
