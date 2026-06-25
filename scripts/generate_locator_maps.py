#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET


REPO_ROOT = Path(__file__).resolve().parents[1]
REGION_CSV = REPO_ROOT / "data/raw/us_regions_notes_seed.csv"
DIVISION_CSV = REPO_ROOT / "data/raw/us_divisions_notes_seed.csv"
BLANK_MAP = REPO_ROOT / "media/blank/us_blank_map_states_only.svg"
REGION_OUTPUT_DIR = REPO_ROOT / "media/locator/regions"
DIVISION_OUTPUT_DIR = REPO_ROOT / "media/locator/divisions"
REGION_MEMBERSHIP_OUTPUT_DIR = REPO_ROOT / "media/membership/regions"
DIVISION_MEMBERSHIP_OUTPUT_DIR = REPO_ROOT / "media/membership/divisions"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

HIGHLIGHT_FILL = "#356d2e"
DEFAULT_FILL = "#f4f1e9"
DEFAULT_STROKE = "#ffffff"
DEFAULT_STROKE_WIDTH = "1.5"
DIVISION_PALETTE = [
    "#2f6a3a",
    "#3e7aa8",
    "#b6924b",
    "#a75c3d",
]
STATE_PALETTE = [
    "#2f6a3a",
    "#4474a3",
    "#b6924b",
    "#a75c3d",
    "#7a5fa1",
    "#9b8748",
    "#3f8f7d",
    "#a14f6b",
    "#5e7f2b",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_codes(value: str) -> set[str]:
    return {part.strip().upper() for part in value.split("|") if part.strip()}


def local_name(tag: str) -> str:
    return tag.split("}", 1)[1] if "}" in tag else tag


def state_code_for_element(element: ET.Element) -> str | None:
    raw_class = (element.get("class") or "").strip()
    if not raw_class:
        return None
    for token in raw_class.split():
        if len(token) == 2 and token.isalpha():
            return token.upper()
    return None


def state_elements(root: ET.Element) -> list[ET.Element]:
    out: list[ET.Element] = []
    for element in root.iter():
        if state_code_for_element(element) is None:
            continue
        if local_name(element.tag) not in {"path", "polygon", "rect", "circle", "ellipse"}:
            continue
        out.append(element)
    return out


def validate_codes(output_name: str, root: ET.Element, state_codes: set[str]) -> None:
    present_codes = {code for element in state_elements(root) if (code := state_code_for_element(element))}
    missing_codes = sorted(code for code in state_codes if code not in present_codes)
    if missing_codes:
        raise ValueError(
            f"{output_name}: missing state classes in blank map: {', '.join(missing_codes)}"
        )


def reset_svg_title(root: ET.Element, title: str, desc: str) -> None:
    root.set("aria-label", title)
    for child in list(root):
        if local_name(child.tag) in {"title", "desc"}:
            root.remove(child)
    title_el = ET.Element(f"{{{SVG_NS}}}title")
    title_el.text = title
    desc_el = ET.Element(f"{{{SVG_NS}}}desc")
    desc_el.text = desc
    root.insert(0, desc_el)
    root.insert(0, title_el)


def write_locator(source_svg: Path, output_path: Path, title: str, state_codes: set[str]) -> None:
    tree = ET.parse(source_svg)
    root = tree.getroot()

    validate_codes(output_path.name, root, state_codes)

    for element in state_elements(root):
        state_code = state_code_for_element(element)
        if state_code in state_codes:
            element.set("fill", HIGHLIGHT_FILL)
        else:
            element.set("fill", DEFAULT_FILL)
        element.set("stroke", DEFAULT_STROKE)
        element.set("stroke-width", DEFAULT_STROKE_WIDTH)

    reset_svg_title(root, title, f"Locator map highlighting {title}.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def write_palette_map(
    source_svg: Path,
    output_path: Path,
    title: str,
    state_to_fill: dict[str, str],
    desc: str,
) -> None:
    tree = ET.parse(source_svg)
    root = tree.getroot()

    validate_codes(output_path.name, root, set(state_to_fill))

    for element in state_elements(root):
        state_code = state_code_for_element(element)
        if state_code is None:
            continue
        element.set("fill", state_to_fill.get(state_code, DEFAULT_FILL))
        element.set("stroke", DEFAULT_STROKE)
        element.set("stroke-width", DEFAULT_STROKE_WIDTH)

    reset_svg_title(root, title, desc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def generate_group(rows: list[dict[str, str]], name_field: str, output_dir: Path) -> int:
    written = 0
    for row in rows:
        name = (row.get(name_field) or "").strip()
        if not name:
            continue
        state_codes = parse_codes(row.get("member_state_codes") or "")
        if not state_codes:
            continue
        filename = f"{slugify(name)}_locator.svg"
        output_path = output_dir / filename
        write_locator(BLANK_MAP, output_path, name, state_codes)
        print(f"write {output_path.relative_to(REPO_ROOT)}")
        written += 1
    return written


def build_region_division_membership_maps(
    region_rows: list[dict[str, str]],
    division_rows: list[dict[str, str]],
) -> int:
    divisions_by_region: dict[str, list[dict[str, str]]] = {}
    for row in division_rows:
        region_name = (row.get("region_name") or "").strip()
        divisions_by_region.setdefault(region_name, []).append(row)

    written = 0
    for region_row in region_rows:
        region_name = (region_row.get("region_name") or "").strip()
        if not region_name:
            continue
        color_map: dict[str, str] = {}
        for index, division_row in enumerate(divisions_by_region.get(region_name, [])):
            fill = DIVISION_PALETTE[index % len(DIVISION_PALETTE)]
            for code in parse_codes(division_row.get("member_state_codes") or ""):
                color_map[code] = fill
        if not color_map:
            continue
        output_path = REGION_MEMBERSHIP_OUTPUT_DIR / f"{slugify(region_name)}_divisions_map.svg"
        write_palette_map(
            BLANK_MAP,
            output_path,
            f"{region_name} divisions",
            color_map,
            f"Unlabeled map showing the Census divisions within {region_name}.",
        )
        print(f"write {output_path.relative_to(REPO_ROOT)}")
        written += 1
    return written


def build_division_state_membership_maps(division_rows: list[dict[str, str]]) -> int:
    written = 0
    for division_row in division_rows:
        division_name = (division_row.get("division_name") or "").strip()
        if not division_name:
            continue
        color_map: dict[str, str] = {}
        for index, code in enumerate(split_codes(division_row.get("member_state_codes") or "")):
            color_map[code] = STATE_PALETTE[index % len(STATE_PALETTE)]
        if not color_map:
            continue
        output_path = DIVISION_MEMBERSHIP_OUTPUT_DIR / f"{slugify(division_name)}_states_map.svg"
        write_palette_map(
            BLANK_MAP,
            output_path,
            f"{division_name} states",
            color_map,
            f"Unlabeled map showing the states in {division_name}.",
        )
        print(f"write {output_path.relative_to(REPO_ROOT)}")
        written += 1
    return written


def split_codes(value: str) -> list[str]:
    return [part.strip().upper() for part in value.split("|") if part.strip()]


def main() -> int:
    if not BLANK_MAP.exists():
        raise FileNotFoundError(
            f"Blank map not found at {BLANK_MAP}. Run scripts/fetch_map_assets.py first."
        )

    regions = read_rows(REGION_CSV)
    divisions = read_rows(DIVISION_CSV)

    region_count = generate_group(regions, "region_name", REGION_OUTPUT_DIR)
    division_count = generate_group(divisions, "division_name", DIVISION_OUTPUT_DIR)
    region_membership_count = build_region_division_membership_maps(regions, divisions)
    division_membership_count = build_division_state_membership_maps(divisions)

    print(
        "done: "
        f"regions={region_count} "
        f"divisions={division_count} "
        f"region_membership_maps={region_membership_count} "
        f"division_membership_maps={division_membership_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
