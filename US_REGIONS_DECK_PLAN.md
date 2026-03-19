# U.S. Regions Deck Plan

## Goal

Build an Anki deck that teaches the U.S. Census Bureau's four regions and nine divisions using two separate note types.

## Scope Decision

This repo uses the Census Bureau hierarchy shown on the linked Wikipedia page:

- Regions: `Northeast`, `Midwest`, `South`, `West`
- Divisions: `New England`, `Mid-Atlantic`, `East North Central`, `West North Central`, `South Atlantic`, `East South Central`, `West South Central`, `Mountain`, `Pacific`

Out of scope for the core deck unless we explicitly expand later:

- unofficial U.S. regions
- Federal Reserve districts
- BEA regions
- U.S. territories that are not assigned to a Census region or division

## Note Types

### 1. Region Note Type

Purpose:

- teach the four top-level Census regions
- reinforce both verbal geography and locator-map recognition

Cards:

1. `Region -> Neighboring regions / countries / oceans`
2. `Region + blank map -> locator map`
3. `Locator map -> region name`
4. `Region -> divisions`

Minimum fields:

- `region_name`
- `blank_map`
- `locator_map`
- `neighboring_regions`
- `neighboring_countries`
- `neighboring_oceans`
- `member_divisions`
- `member_states`
- `source_notes`

### 2. Division Note Type

Purpose:

- teach the nine Census divisions and their parent regions
- reinforce division recognition from locator maps
- connect each division to the state-level border patterns that make the map memorable

Cards:

1. `Division -> Region`
2. `Division -> neighboring divisions / countries / oceans`
3. `Division + blank map -> locator map`
4. `Locator map -> division`
5. `Division -> per-state border summary`

Minimum fields:

- `division_name`
- `region_name`
- `blank_map`
- `locator_map`
- `neighboring_divisions`
- `neighboring_countries`
- `neighboring_oceans`
- `member_states`
- `state_border_summary`
- `source_notes`

## Data Model Decisions

1. Keep `regions` and `divisions` as separate notes instead of squeezing everything into one note type.
2. Preserve both `member_divisions` and `member_states` on region notes so region cards can stay useful even if division cards are temporarily incomplete.
3. Store border summaries as human-readable text first; later we can derive chips or grouped HTML blocks at build time.
4. Treat oceans and countries as first-class neighbors because they are part of the memory target, not just decorative notes.
5. Use a shared `blank_map` field so every map-recognition card starts from the same base visual.

## Data Files

Initial scaffold files:

- [`data/raw/us_regions_notes_seed.csv`](data/raw/us_regions_notes_seed.csv)
- [`data/raw/us_divisions_notes_seed.csv`](data/raw/us_divisions_notes_seed.csv)

Planned follow-up files:

- a media manifest for blank and locator maps
- a state border reference table used to generate `state_border_summary`

## Media Plan

We need two families of map assets:

1. One shared blank U.S. base map suitable for both region and division cards
2. Locator maps for each of the four regions and nine divisions

Preferred asset characteristics:

- vector-first when possible
- consistent projection and aspect ratio
- easy to read at Anki card size
- no clutter from labels that reveal the answer too early

## Milestones

1. Confirm the hierarchy and seed the raw region and division tables.
2. Identify reusable blank-map and locator-map assets, ideally from Wikimedia Commons or Census-derived public sources.
3. Add a state border reference layer for the division notes.
4. Build APKG generation scripts and note templates.
5. Export and review the first deck package.

## Open Questions

1. Whether to show `Gulf of Mexico` explicitly as a neighboring water body on South and West South Central cards, or normalize to a broader ocean/coast phrasing.
2. Whether Alaska and Hawaii should share the same locator-map visual treatment as the contiguous states or use insets.
3. Whether `state_border_summary` should be kept as one multiline field or split into one field per state at build time.
