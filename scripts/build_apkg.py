#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import re
from pathlib import Path

import genanki


REPO_ROOT = Path(__file__).resolve().parents[1]
REGION_CSV = REPO_ROOT / "data/raw/us_regions_notes_seed.csv"
DIVISION_CSV = REPO_ROOT / "data/raw/us_divisions_notes_seed.csv"
OUTPUT_APKG = REPO_ROOT / "out/us-regions.apkg"

BLANK_MAP_FILENAME = "us_blank_map_states_only.svg"
BLANK_MAP_PATH = REPO_ROOT / "media/blank" / BLANK_MAP_FILENAME
REGION_LOCATOR_DIR = REPO_ROOT / "media/locator/regions"
DIVISION_LOCATOR_DIR = REPO_ROOT / "media/locator/divisions"
REGION_MEMBERSHIP_DIR = REPO_ROOT / "media/membership/regions"
DIVISION_MEMBERSHIP_DIR = REPO_ROOT / "media/membership/divisions"

REGION_MODEL_ID = 1_893_420_211
DIVISION_MODEL_ID = 1_893_420_212
DECK_ID = 1_893_420_213


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def split_pipe_values(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def split_summary_lines(value: str) -> list[str]:
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


def make_map_html(filename: str, alt_text: str) -> str:
    return (
        '<div class="map-frame">'
        f'<img class="map-image" src="{html.escape(filename)}" alt="{html.escape(alt_text)}">'
        "</div>"
    )


def make_compact_map_html(filename: str, alt_text: str) -> str:
    return (
        '<div class="map-frame map-frame-compact">'
        f'<img class="map-image" src="{html.escape(filename)}" alt="{html.escape(alt_text)}">'
        "</div>"
    )


def html_chip_group(title: str, items: list[str]) -> str:
    if not items:
        return ""
    chips = "".join(f'<span class="chip">{html.escape(item)}</span>' for item in items)
    return (
        '<div class="fact-panel">'
        f'<div class="fact-title">{html.escape(title)}</div>'
        f'<div class="chips">{chips}</div>'
        "</div>"
    )


def html_member_list(title: str, items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return (
        '<div class="fact-panel">'
        f'<div class="fact-title">{html.escape(title)}</div>'
        f'<ul class="detail-list">{lis}</ul>'
        "</div>"
    )


def html_neighbor_sections(
    regions_or_divisions_label: str,
    first_group: list[str],
    countries: list[str],
    oceans: list[str],
) -> str:
    parts = [
        html_chip_group(regions_or_divisions_label, first_group),
        html_chip_group("Countries", countries),
        html_chip_group("Oceans", oceans),
    ]
    return "".join(part for part in parts if part)


def html_state_border_rows(lines: list[str]) -> str:
    if not lines:
        return ""
    rows: list[str] = []
    for line in lines:
        if ":" in line:
            state_name, details = line.split(":", 1)
            rows.append(
                '<div class="border-row">'
                f'<div class="border-state">{html.escape(state_name.strip())}</div>'
                f'<div class="border-details">{html.escape(details.strip())}</div>'
                "</div>"
            )
        else:
            rows.append(f'<div class="border-row"><div class="border-details">{html.escape(line)}</div></div>')
    return '<div class="border-grid">' + "".join(rows) + "</div>"


def shared_css() -> str:
    return """:root{
  --paper:#f8f3e7;
  --paper-deep:#e7dac3;
  --ink:#1c1b19;
  --muted:#5f5a52;
  --navy:#1f3a5f;
  --navy-soft:#dbe5f1;
  --red:#9e3d34;
  --red-soft:#f0ddd8;
  --gold:#b6934f;
  --pine:#355742;
  --pine-soft:#dce8df;
  --rule:rgba(35,30,23,0.14);
  --shadow:rgba(32,24,15,0.16);
}
.card{
  font-family:"Baskerville","Iowan Old Style","Palatino Linotype","Book Antiqua",serif;
  color:var(--ink);
  background:
    radial-gradient(circle at top left, rgba(182,147,79,0.16), transparent 28%),
    radial-gradient(circle at bottom right, rgba(31,58,95,0.10), transparent 30%),
    linear-gradient(180deg, #fcf8f1 0%, var(--paper) 52%, #efe3cf 100%);
  font-size:20px;
  line-height:1.42;
  padding:22px 18px 28px;
}
.wrap{
  max-width:780px;
  margin:0 auto;
}
.plate{
  background:
    linear-gradient(180deg, rgba(255,255,255,0.72), rgba(255,255,255,0.38));
  border:1px solid var(--rule);
  border-radius:26px;
  padding:22px 22px 24px;
  box-shadow:0 18px 40px var(--shadow);
  position:relative;
}
.plate::before{
  content:"";
  position:absolute;
  inset:10px;
  border:1px solid rgba(182,147,79,0.18);
  border-radius:18px;
  pointer-events:none;
}
.eyebrow{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  text-transform:uppercase;
  letter-spacing:0.16em;
  font-size:11px;
  color:var(--navy);
  margin:0 0 10px;
}
.title{
  font-size:50px;
  line-height:0.98;
  letter-spacing:-0.03em;
  margin:0;
  color:var(--navy);
}
.subtitle{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  color:var(--muted);
  font-size:18px;
  margin-top:10px;
}
.prompt{
  margin-top:18px;
  padding-top:16px;
  border-top:1px solid var(--rule);
  color:var(--muted);
  font-size:17px;
}
.answer-panel{
  margin-top:18px;
  border-radius:22px;
  border:1px solid rgba(31,58,95,0.16);
  background:
    linear-gradient(180deg, rgba(31,58,95,0.08), rgba(255,255,255,0.66));
  padding:18px 18px 16px;
}
.answer-label{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  text-transform:uppercase;
  letter-spacing:0.14em;
  font-size:11px;
  color:var(--red);
  margin:0 0 8px;
}
.answer-main{
  font-size:34px;
  line-height:1.06;
  margin:0;
  color:var(--navy);
}
.meta-grid{
  display:grid;
  gap:16px;
  margin-top:18px;
}
@media (min-width:720px){
  .meta-grid{
    grid-template-columns:1fr 1fr;
  }
}
.fact-panel,
.border-row{
  border:1px solid var(--rule);
  border-radius:18px;
  background:rgba(255,255,255,0.56);
  padding:15px 16px 14px;
}
.fact-title{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:12px;
  text-transform:uppercase;
  letter-spacing:0.12em;
  color:var(--pine);
  margin:0 0 10px;
}
.chips{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
}
.chip{
  display:inline-flex;
  align-items:center;
  border-radius:999px;
  padding:7px 12px;
  background:linear-gradient(180deg, var(--navy-soft), #eef3f9);
  color:var(--navy);
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:14px;
  border:1px solid rgba(31,58,95,0.10);
}
.detail-list{
  margin:0;
  padding-left:18px;
}
.detail-list li{
  margin:0 0 8px;
}
.map-frame{
  margin-top:18px;
  border-radius:22px;
  border:1px solid var(--rule);
  background:
    linear-gradient(180deg, rgba(255,255,255,0.82), rgba(242,236,225,0.82));
  padding:16px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,0.5);
}
.map-frame-compact{
  margin-top:16px;
}
.map-image{
  display:block;
  width:100%;
  max-width:100%;
  height:auto;
  filter:saturate(0.95) contrast(1.02);
}
.border-grid{
  display:grid;
  gap:12px;
  margin-top:18px;
}
.border-state{
  font-size:20px;
  color:var(--red);
  margin:0 0 6px;
}
.border-details{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:15px;
  color:var(--muted);
  white-space:pre-wrap;
}

.wiki-panel{
  margin-top:18px;
  border:1px solid var(--rule);
  border-radius:18px;
  background:rgba(255,255,255,0.56);
  padding:15px 16px 14px;
}

.wiki-frame{
  display:block;
  width:100%;
  height:420px;
  border:1px solid rgba(31,58,95,0.12);
  border-radius:14px;
  background:rgba(255,255,255,0.82);
}

.wiki-link{
  display:inline-block;
  margin-top:10px;
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:14px;
  color:var(--navy);
  text-decoration:none;
}

.wiki-link:hover{
  text-decoration:underline;
}
"""


def division_css() -> str:
    return """
:root{
  --paper:#f7f2e7;
  --paper-deep:#e7dbc7;
  --ink:#1f1a16;
  --muted:#65584c;
  --forest:#2f6a3a;
  --forest-soft:#dfeada;
  --navy:#21486d;
  --rust:#9a5135;
  --gold:#b6924b;
  --rule:rgba(43,31,20,0.14);
  --shadow:rgba(40,27,14,0.16);
}
.card{
  font-family:"Baskerville","Iowan Old Style","Palatino Linotype","Book Antiqua",serif;
  color:var(--ink);
  background:
    radial-gradient(circle at top left, rgba(182,146,75,0.14), transparent 30%),
    radial-gradient(circle at bottom right, rgba(33,72,109,0.12), transparent 28%),
    linear-gradient(180deg, #fcf8f1 0%, var(--paper) 54%, #f0e5d4 100%);
  font-size:20px;
  line-height:1.42;
  padding:22px 18px 28px;
}
.wrap{
  max-width:780px;
  margin:0 auto;
}
.plate{
  background:linear-gradient(180deg, rgba(255,255,255,0.68), rgba(255,255,255,0.34));
  border:1px solid var(--rule);
  border-radius:26px;
  padding:22px 22px 24px;
  box-shadow:0 18px 40px var(--shadow);
}
.eyebrow{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  text-transform:uppercase;
  letter-spacing:0.16em;
  font-size:11px;
  color:var(--forest);
  margin:0 0 10px;
}
.title{
  font-size:50px;
  line-height:0.98;
  letter-spacing:-0.03em;
  margin:0;
}
.subtitle{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  color:var(--muted);
  font-size:18px;
  margin-top:10px;
}
.prompt{
  margin-top:18px;
  padding-top:16px;
  border-top:1px solid var(--rule);
  color:var(--muted);
  font-size:17px;
}
.answer-panel{
  margin-top:18px;
  border-radius:22px;
  border:1px solid rgba(47,106,58,0.18);
  background:linear-gradient(180deg, rgba(47,106,58,0.10), rgba(255,255,255,0.65));
  padding:18px 18px 16px;
}
.answer-label{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  text-transform:uppercase;
  letter-spacing:0.14em;
  font-size:11px;
  color:var(--rust);
  margin:0 0 8px;
}
.answer-main{
  font-size:34px;
  line-height:1.06;
  margin:0;
}
.meta-grid{
  display:grid;
  gap:16px;
  margin-top:18px;
}
@media (min-width:720px){
  .meta-grid{
    grid-template-columns:1fr 1fr;
  }
}
.fact-panel{
  border:1px solid var(--rule);
  border-radius:18px;
  background:rgba(255,255,255,0.52);
  padding:15px 16px 14px;
}
.fact-title{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:12px;
  text-transform:uppercase;
  letter-spacing:0.12em;
  color:var(--navy);
  margin:0 0 10px;
}
.chips{
  display:flex;
  flex-wrap:wrap;
  gap:10px;
}
.chip{
  display:inline-flex;
  align-items:center;
  border-radius:999px;
  padding:7px 12px;
  background:var(--forest-soft);
  color:#1f3c25;
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:14px;
}
.detail-list{
  margin:0;
  padding-left:18px;
}
.detail-list li{
  margin:0 0 8px;
}
.map-frame{
  margin-top:18px;
  border-radius:22px;
  border:1px solid var(--rule);
  background:linear-gradient(180deg, rgba(255,255,255,0.78), rgba(244,238,227,0.78));
  padding:16px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,0.5);
}
.map-frame-compact{
  margin-top:16px;
}
.map-image{
  display:block;
  width:100%;
  max-width:100%;
  height:auto;
}
.border-grid{
  display:grid;
  gap:12px;
  margin-top:18px;
}
.border-row{
  border:1px solid var(--rule);
  border-radius:16px;
  background:rgba(255,255,255,0.52);
  padding:14px 15px 13px;
}
.border-state{
  font-size:20px;
  color:var(--navy);
  margin:0 0 6px;
}
.border-details{
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:15px;
  color:var(--muted);
  white-space:pre-wrap;
}

.wiki-panel{
  margin-top:18px;
  border:1px solid var(--rule);
  border-radius:18px;
  background:rgba(255,255,255,0.52);
  padding:15px 16px 14px;
}

.wiki-frame{
  display:block;
  width:100%;
  height:420px;
  border:1px solid rgba(33,72,109,0.12);
  border-radius:14px;
  background:rgba(255,255,255,0.82);
}

.wiki-link{
  display:inline-block;
  margin-top:10px;
  font-family:"Avenir Next","Gill Sans","Trebuchet MS",sans-serif;
  font-size:14px;
  color:var(--navy);
  text-decoration:none;
}

.wiki-link:hover{
  text-decoration:underline;
}
"""


def region_fieldnames() -> list[str]:
    return [
        "region_name",
        "blank_map",
        "locator_map",
        "neighboring_regions",
        "neighboring_countries",
        "neighboring_oceans",
        "member_divisions",
        "member_states",
        "member_state_codes",
        "source_notes",
        "Card_Neighbors_HTML",
        "Card_Divisions_HTML",
        "Card_MemberStates_HTML",
        "Card_BlankMap_HTML",
        "Card_LocatorMap_HTML",
        "Card_DivisionsMap_HTML",
        "Wikipedia",
    ]


def division_fieldnames() -> list[str]:
    return [
        "division_name",
        "region_name",
        "blank_map",
        "locator_map",
        "neighboring_divisions",
        "neighboring_countries",
        "neighboring_oceans",
        "member_states",
        "member_state_codes",
        "state_border_summary",
        "source_notes",
        "Card_Neighbors_HTML",
        "Card_StateBorders_HTML",
        "Card_MemberStates_HTML",
        "Card_BlankMap_HTML",
        "Card_LocatorMap_HTML",
        "Card_StatesMap_HTML",
        "Wikipedia",
    ]


def region_model() -> genanki.Model:
    return genanki.Model(
        REGION_MODEL_ID,
        "U.S. Region+",
        fields=[{"name": name} for name in region_fieldnames()],
        templates=[
            {
                "name": "Region -> Neighbors",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">U.S. Census Region</div>
  <h1 class="title">{{region_name}}</h1>
  <div class="prompt">Which regions, countries, and oceans border this region?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Borders</div>
  <div class="meta-grid">{{Card_Neighbors_HTML}}</div>
  {{Card_DivisionsMap_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Region + Blank -> Locator",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Locate The Region</div>
  <h1 class="title">{{region_name}}</h1>
  <div class="prompt">Recognize the region from the shared blank map, then reveal the locator map.</div>
  {{Card_BlankMap_HTML}}
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Locator Map</div>
  {{Card_LocatorMap_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Locator -> Region",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Name The Region</div>
  {{Card_LocatorMap_HTML}}
  <div class="prompt">Which U.S. Census region is highlighted here?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Answer</div>
  <div class="answer-main">{{region_name}}</div>
  <div class="meta-grid">{{Card_Divisions_HTML}}{{Card_MemberStates_HTML}}</div>
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Region -> Divisions",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Member Divisions</div>
  <h1 class="title">{{region_name}}</h1>
  <div class="prompt">Which Census divisions belong to this region?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Divisions</div>
  <div class="meta-grid">{{Card_Divisions_HTML}}</div>
  {{Card_DivisionsMap_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
        ],
        css=shared_css(),
    )


def division_model() -> genanki.Model:
    return genanki.Model(
        DIVISION_MODEL_ID,
        "U.S. Division+",
        fields=[{"name": name} for name in division_fieldnames()],
        templates=[
            {
                "name": "Division -> Region",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">U.S. Census Division</div>
  <h1 class="title">{{division_name}}</h1>
  <div class="prompt">Which U.S. Census region contains this division?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Region</div>
  <div class="answer-main">{{region_name}}</div>
  <div class="meta-grid">{{Card_MemberStates_HTML}}</div>
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Division -> Neighbors",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Division Borders</div>
  <h1 class="title">{{division_name}}</h1>
  <div class="subtitle">{{region_name}}</div>
  <div class="prompt">Which divisions, countries, and oceans border this division?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Borders</div>
  <div class="meta-grid">{{Card_Neighbors_HTML}}</div>
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Division + Blank -> Locator",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Locate The Division</div>
  <h1 class="title">{{division_name}}</h1>
  <div class="subtitle">{{region_name}}</div>
  <div class="prompt">Start from the blank map, then reveal the highlighted division.</div>
  {{Card_BlankMap_HTML}}
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Locator Map</div>
  {{Card_LocatorMap_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Locator -> Division",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Name The Division</div>
  {{Card_LocatorMap_HTML}}
  <div class="prompt">Which U.S. Census division is highlighted here?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Answer</div>
  <div class="answer-main">{{division_name}}</div>
  <div class="subtitle">{{region_name}}</div>
  <div class="meta-grid">{{Card_MemberStates_HTML}}</div>
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Division -> States",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">Member States</div>
  <h1 class="title">{{division_name}}</h1>
  <div class="subtitle">{{region_name}}</div>
  <div class="prompt">What states belong to this division?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">States</div>
  <div class="meta-grid">{{Card_MemberStates_HTML}}</div>
  {{Card_StatesMap_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
            {
                "name": "Division -> State Borders",
                "qfmt": """
<div class="wrap"><div class="plate">
  <div class="eyebrow">State Borders</div>
  <h1 class="title">{{division_name}}</h1>
  <div class="subtitle">{{region_name}}</div>
  <div class="prompt">For each member state, which states, countries, and oceans does it border?</div>
</div></div>
""",
                "afmt": """
{{FrontSide}}
<div class="wrap"><div class="answer-panel">
  <div class="answer-label">Per-State Borders</div>
  {{Card_StateBorders_HTML}}
</div>

{{#Wikipedia}}
<div class="wiki-panel">
  <div class="fact-title">Wikipedia</div>
  <iframe class="wiki-frame" src="{{Wikipedia}}"></iframe>
  <a class="wiki-link" href="{{Wikipedia}}">Open in browser</a>
</div>
{{/Wikipedia}}
</div>
""",
            },
        ],
        css=division_css(),
    )


def make_region_note(model: genanki.Model, row: dict[str, str]) -> genanki.Note:
    name = (row.get("region_name") or "").strip()
    blank_filename = BLANK_MAP_FILENAME
    locator_filename = f"{slugify(name)}_locator.svg"
    divisions_map_filename = f"{slugify(name)}_divisions_map.svg"
    divisions = split_pipe_values(row.get("member_divisions") or "")
    states = split_pipe_values(row.get("member_states") or "")
    neighbors = split_pipe_values(row.get("neighboring_regions") or "")
    countries = split_pipe_values(row.get("neighboring_countries") or "")
    oceans = split_pipe_values(row.get("neighboring_oceans") or "")

    fields = [
        name,
        blank_filename,
        locator_filename,
        row.get("neighboring_regions") or "",
        row.get("neighboring_countries") or "",
        row.get("neighboring_oceans") or "",
        row.get("member_divisions") or "",
        row.get("member_states") or "",
        row.get("member_state_codes") or "",
        row.get("source_notes") or "",
        html_neighbor_sections("Neighboring Regions", neighbors, countries, oceans),
        html_chip_group("Member Divisions", divisions),
        html_member_list("Member States", states),
        make_map_html(blank_filename, f"Blank U.S. map for {name}"),
        make_map_html(locator_filename, f"Locator map for {name}"),
        make_compact_map_html(divisions_map_filename, f"Division map for {name}"),
        row.get("Wikipedia") or "",
    ]
    return genanki.Note(model=model, fields=fields, guid=genanki.guid_for("region", name))


def make_division_note(model: genanki.Model, row: dict[str, str]) -> genanki.Note:
    name = (row.get("division_name") or "").strip()
    blank_filename = BLANK_MAP_FILENAME
    locator_filename = f"{slugify(name)}_locator.svg"
    states_map_filename = f"{slugify(name)}_states_map.svg"
    states = split_pipe_values(row.get("member_states") or "")
    neighbors = split_pipe_values(row.get("neighboring_divisions") or "")
    countries = split_pipe_values(row.get("neighboring_countries") or "")
    oceans = split_pipe_values(row.get("neighboring_oceans") or "")
    state_border_lines = split_summary_lines(row.get("state_border_summary") or "")

    fields = [
        name,
        row.get("region_name") or "",
        blank_filename,
        locator_filename,
        row.get("neighboring_divisions") or "",
        row.get("neighboring_countries") or "",
        row.get("neighboring_oceans") or "",
        row.get("member_states") or "",
        row.get("member_state_codes") or "",
        row.get("state_border_summary") or "",
        row.get("source_notes") or "",
        html_neighbor_sections("Neighboring Divisions", neighbors, countries, oceans),
        html_state_border_rows(state_border_lines),
        html_member_list("Member States", states),
        make_map_html(blank_filename, f"Blank U.S. map for {name}"),
        make_map_html(locator_filename, f"Locator map for {name}"),
        make_compact_map_html(states_map_filename, f"State membership map for {name}"),
        row.get("Wikipedia") or "",
    ]
    return genanki.Note(model=model, fields=fields, guid=genanki.guid_for("division", name))


def collect_media(region_rows: list[dict[str, str]], division_rows: list[dict[str, str]]) -> list[str]:
    media: list[Path] = []
    if BLANK_MAP_PATH.exists():
        media.append(BLANK_MAP_PATH)
    for row in region_rows:
        name = (row.get("region_name") or "").strip()
        if not name:
            continue
        path = REGION_LOCATOR_DIR / f"{slugify(name)}_locator.svg"
        if path.exists():
            media.append(path)
        membership_path = REGION_MEMBERSHIP_DIR / f"{slugify(name)}_divisions_map.svg"
        if membership_path.exists():
            media.append(membership_path)
    for row in division_rows:
        name = (row.get("division_name") or "").strip()
        if not name:
            continue
        path = DIVISION_LOCATOR_DIR / f"{slugify(name)}_locator.svg"
        if path.exists():
            media.append(path)
        membership_path = DIVISION_MEMBERSHIP_DIR / f"{slugify(name)}_states_map.svg"
        if membership_path.exists():
            media.append(membership_path)
    return [str(path) for path in sorted(dict.fromkeys(media))]


def main() -> int:
    region_rows = read_rows(REGION_CSV)
    division_rows = read_rows(DIVISION_CSV)

    deck = genanki.Deck(
        DECK_ID,
        "U.S. Regions and Divisions",
        description="U.S. Census regions and divisions with locator-map recognition cards.",
    )

    region_note_model = region_model()
    division_note_model = division_model()

    for row in region_rows:
        deck.add_note(make_region_note(region_note_model, row))
    for row in division_rows:
        deck.add_note(make_division_note(division_note_model, row))

    OUTPUT_APKG.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package(deck)
    package.media_files = collect_media(region_rows, division_rows)
    package.write_to_file(str(OUTPUT_APKG))
    print(f"wrote {OUTPUT_APKG.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
