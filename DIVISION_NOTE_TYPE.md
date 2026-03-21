# Division Note Type

## Fields

1. `division_name`
   The Census division name, for example `West North Central`.
2. `region_name`
   Parent Census region.
3. `blank_map`
   Shared base-map asset used on map-prompt cards.
4. `locator_map`
   Division-specific locator map.
5. `neighboring_divisions`
   Other Census divisions that touch this division through at least one member state.
6. `neighboring_countries`
   Countries bordering the division.
7. `neighboring_oceans`
   Oceans or named coast-facing bodies of water we decide to treat as deck-relevant neighbors.
8. `member_states`
   Comma-separated states plus the District of Columbia where applicable.
9. `member_state_codes`
   Pipe-separated USPS state codes used to generate locator maps from the blank SVG.
10. `state_border_summary`
   Multiline field describing, for each member state, the states, countries, and oceans it borders.
11. `source_notes`
   Provenance and caveats for the note.

## Card Templates

1. `Division -> Region`
2. `Division -> Neighboring divisions / countries / oceans`
3. `Division + Blank Map -> Locator Map`
4. `Locator Map -> Division`
5. `Division -> Per-state border summary`

## Build Notes

The current plan is to derive locator maps from a single blank U.S. SVG whose state paths are keyed by two-letter abbreviations.
