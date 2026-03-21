#!/usr/bin/env python3
from __future__ import annotations

import csv
import time
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_CSV = REPO_ROOT / "data/raw/us_map_asset_sources.csv"

DEST_BY_ASSET_ID = {
    "blank_us_map_states_only": REPO_ROOT / "media/blank/us_blank_map_states_only.svg",
    "us_census_geographical_region_map": REPO_ROOT / "media/reference/us_census_geographical_region_map.svg",
    "garm_figure_6_1": REPO_ROOT / "media/reference/geographic_areas_reference_manual_figure_6_1.png",
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def download(url: str, dest: Path) -> None:
    last_error: Exception | None = None
    for attempt in range(4):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "image/svg+xml,image/*;q=0.9,*/*;q=0.8",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(response.read())
                return
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code != 429 or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After")
            wait_seconds = max(2, 2 * (attempt + 1))
            if retry_after and retry_after.isdigit():
                wait_seconds = max(wait_seconds, int(retry_after))
            time.sleep(wait_seconds)
        except Exception as error:
            last_error = error
            if attempt == 3:
                raise
            time.sleep(max(2, attempt + 1))

    if last_error is not None:
        raise last_error
    raise RuntimeError(f"Failed to download {url}")


def main() -> int:
    rows = read_rows(SOURCE_CSV)
    downloaded = 0
    skipped = 0

    for row in rows:
        asset_id = (row.get("asset_id") or "").strip()
        url = (row.get("download_url") or "").strip()
        dest = DEST_BY_ASSET_ID.get(asset_id)
        if not asset_id or not url or dest is None:
            continue
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            print(f"skip  {dest.relative_to(REPO_ROOT)}")
            continue

        print(f"fetch {dest.relative_to(REPO_ROOT)}")
        download(url, dest)
        downloaded += 1
        time.sleep(1.0)

    print(f"done: downloaded={downloaded} skipped={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
