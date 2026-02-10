# etl/02_ingest_country.py
from __future__ import annotations

from pathlib import Path
import pandas as pd

OWID_URL = "https://owid-public.owid.io/data/co2/owid-co2-data.csv"
RAW_CACHE = Path("data/raw/owid-co2-data.csv")
OUT_PATH = Path("data/processed/country_co2_yearly.csv")

YEAR_MIN = 1750
YEAR_MAX = 2020


def fetch_owid_csv(url: str, cache_path: Path) -> Path:
    """
    Downloads OWID CSV with a browser-like User-Agent to avoid 403.
    Falls back to cached file if present.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import requests  # keep optional if not installed

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        }
        with requests.get(url, headers=headers, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(cache_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
        return cache_path

    except Exception as e:
        if cache_path.exists():
            print(f"⚠️ Download failed ({e}). Using cached file: {cache_path}")
            return cache_path
        raise


def main() -> None:
    csv_path = fetch_owid_csv(OWID_URL, RAW_CACHE)
    df = pd.read_csv(csv_path)

    # 1) Keep only ISO3 entities
    df = df[df["iso_code"].astype(str).str.len() == 3]

    # 2) Year alignment
    df = df[(df["year"] >= YEAR_MIN) & (df["year"] <= YEAR_MAX)]

    # 3) Select + rename (preserve NULLs)
    df = df[["iso_code", "year", "co2", "co2_per_capita"]].rename(
        columns={"iso_code": "iso3", "co2": "co2_total_mt"}
    )

    # 4) Deterministic ordering
    df = df.sort_values(["iso3", "year"], kind="mergesort")

    # 5) Write processed artifact
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"✅ Raw cached at: {csv_path}")
    print(f"✅ Processed written: {OUT_PATH}")
    print(f"Rows: {len(df):,}")
    print(f"Countries (iso3): {df['iso3'].nunique():,}")
    print(f"Year range: {df['year'].min()}–{df['year'].max()}")


if __name__ == "__main__":
    main()
