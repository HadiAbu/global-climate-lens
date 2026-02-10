#!/usr/bin/env bash
set -euo pipefail

CSV_PATH="data/processed/country_co2_yearly.csv"

if [ ! -f "$CSV_PATH" ]; then
  echo "❌ Missing $CSV_PATH. Run: python etl/02_ingest_country.py"
  exit 1
fi

# DATABASE_URL should already exist in your project (your API uses Postgres)
: "${DATABASE_URL:?DATABASE_URL is not set}"

echo "✅ Creating table (if needed)..."
psql "$DATABASE_URL" -f db/sql/04_fact_country_co2_yearly.sql

echo "✅ Loading CSV into fact_country_co2_yearly..."
psql "$DATABASE_URL" -c "\copy fact_country_co2_yearly (iso3,year,co2_total_mt,co2_per_capita) FROM '$CSV_PATH' WITH (FORMAT csv, HEADER true)"

echo "✅ Done."
