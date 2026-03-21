# Media

Planned media layout:

- `blank/` for shared blank U.S. base maps
- `reference/` for labeled reference maps used for QA
- `locator/` for region and division locator maps

Planned scripts:

- `scripts/fetch_map_assets.py` downloads the shared blank map and QA reference images
- `scripts/generate_locator_maps.py` derives region and division locator SVGs from the blank base plus `member_state_codes`
