from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

CSV_PATH = Path("data/processed/country_co2_yearly.csv")

DDL = """
CREATE TABLE IF NOT EXISTS fact_country_co2_yearly (
  iso3 TEXT NOT NULL,
  year INT NOT NULL,
  co2_total_mt NUMERIC,
  co2_per_capita NUMERIC,
  PRIMARY KEY (iso3, year),
  CONSTRAINT fk_fact_country_country
    FOREIGN KEY (iso3) REFERENCES dim_country (iso3)
);
CREATE INDEX IF NOT EXISTS idx_fact_country_co2_yearly_year
  ON fact_country_co2_yearly(year);
"""


def main() -> None:
    database_url = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL_LOCAL or DATABASE_URL is not set")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Missing {CSV_PATH}. Run: python etl/02_ingest_country.py"
        )

    engine = create_engine(database_url)

    # 1) Ensure table exists
    with engine.begin() as conn:
        # execute multiple statements safely
        for stmt in [s.strip() for s in DDL.split(";") if s.strip()]:
            conn.execute(text(stmt))

    # 2) Load CSV via pandas -> SQL (clean + portable)
    df = pd.read_csv(CSV_PATH)

    # 2.5) Filter to countries that exist in dim_country (prevents orphan facts)
    with engine.connect() as conn:
        dim_iso3 = {
            row[0]
            for row in conn.execute(text("SELECT iso3 FROM dim_country")).fetchall()
        }

    before_rows = len(df)
    missing_iso3 = sorted(set(df["iso3"]) - dim_iso3)

    if missing_iso3:
        print(
            f"⚠️ Found {len(missing_iso3)} ISO3 codes not in dim_country. They will be excluded."
        )
        # show a short preview (avoid dumping huge lists)
        print(
            "Missing ISO3 preview:",
            missing_iso3[:25],
            "..." if len(missing_iso3) > 25 else "",
        )
        top_missing = (
            df[df["iso3"].isin(missing_iso3)]
            .groupby("iso3")
            .size()
            .sort_values(ascending=False)
            .head(20)
        )
        print("\nTop missing ISO3 by row count:")
        print(top_missing.to_string())

    df = df[df["iso3"].isin(dim_iso3)]
    after_rows = len(df)

    print(
        f"✅ Filtered facts to dim_country: {before_rows:,} → {after_rows:,} rows (dropped {before_rows - after_rows:,})"
    )

    # Optional: enforce types to avoid surprises
    df["year"] = df["year"].astype(int)

    # 3) Upsert strategy: simplest clean approach is truncate + reload for now
    # (Stage 4 is deterministic; later we can incremental-load if needed)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE fact_country_co2_yearly;"))

    df.to_sql(
        "fact_country_co2_yearly",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )

    print("✅ Loaded fact_country_co2_yearly")
    print(f"Rows inserted: {len(df):,}")


if __name__ == "__main__":
    main()
