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
5. Division -> per-state border summary

## Project Status

The repo is currently a planning and data-seeding scaffold. The next implementation milestones are:

1. verify and fetch reusable blank-map and locator-map assets
2. enrich the division notes with per-state border summaries
3. build an APKG export script
