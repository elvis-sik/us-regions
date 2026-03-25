# us-regions

This repository is a scaffold for an Anki deck about the U.S. Census Bureau's four regions and nine divisions.

Primary source:

- [List of regions of the United States](https://en.wikipedia.org/wiki/List_of_regions_of_the_United_States)

Working assumption for this repo:

- use the Census Bureau's four regions and nine divisions as the canonical hierarchy
- include the District of Columbia with `South Atlantic`
- exclude Puerto Rico and other U.S. territories from the deck's core hierarchy because they are not part of any Census region or division in the linked source

## Note Types

This deck is intentionally split into two note types:

1. Region notes
2. Division notes

The field contracts live in:

- [`REGION_NOTE_TYPE.md`](REGION_NOTE_TYPE.md)
- [`DIVISION_NOTE_TYPE.md`](DIVISION_NOTE_TYPE.md)

The project plan lives in:

- [`US_REGIONS_DECK_PLAN.md`](US_REGIONS_DECK_PLAN.md)

Seed data lives in:

- [`data/raw/us_regions_notes_seed.csv`](data/raw/us_regions_notes_seed.csv)
- [`data/raw/us_divisions_notes_seed.csv`](data/raw/us_divisions_notes_seed.csv)
- [`data/raw/us_map_asset_sources.csv`](data/raw/us_map_asset_sources.csv)
- [`data/raw/us_state_border_reference.csv`](data/raw/us_state_border_reference.csv)

## Initial Scope

Planned region cards:

1. Region -> neighboring regions / countries / oceans
2. Region name + blank map -> locator map
3. Locator map -> region name
4. Region -> divisions

Planned division cards:

1. Division -> region
2. Division -> neighboring divisions / countries / oceans
3. Division name + blank map -> locator map
4. Locator map -> division name
5. Division -> states
6. Division -> per-state border summary

## Project Status

The repo is currently a planning and data-seeding scaffold. The next implementation milestones are:

1. fetch the shared blank map and reference maps from the source manifest
2. generate region and division locator maps from state-code membership
3. enrich the division notes with per-state border summaries
4. build an APKG export script

## Build Workflow

Install the deck-building dependencies:

```sh
uv sync --extra deck
```

Fetch the source map assets:

```sh
.venv/bin/python scripts/fetch_map_assets.py
```

Generate the region and division locator SVGs:

```sh
.venv/bin/python scripts/generate_locator_maps.py
```

That step now also generates unlabeled region-division answer maps and division-state answer maps used on the backs of the membership cards.

Populate the division state-border summaries from the state reference table:

```sh
.venv/bin/python scripts/populate_division_border_summaries.py
```

Build the Anki package:

```sh
.venv/bin/python scripts/build_apkg.py
```

Output:

- `out/us-regions.apkg`
