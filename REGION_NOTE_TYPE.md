# Region Note Type

## Fields

1. `region_name`
   The Census region name, for example `Midwest`.
2. `blank_map`
   Shared base-map asset used on map-prompt cards.
3. `locator_map`
   Region-specific locator map.
4. `neighboring_regions`
   Other Census regions that touch this region.
5. `neighboring_countries`
   Countries bordering the region.
6. `neighboring_oceans`
   Oceans or named coast-facing bodies of water we decide to treat as deck-relevant neighbors.
7. `member_divisions`
   Comma-separated Census divisions within the region.
8. `member_states`
   Comma-separated states plus the District of Columbia where applicable.
9. `source_notes`
   Provenance and caveats for the note.

## Card Templates

1. `Region -> Neighboring regions / countries / oceans`
2. `Region + Blank Map -> Locator Map`
3. `Locator Map -> Region Name`
4. `Region -> Divisions`
