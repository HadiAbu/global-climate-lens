#!/usr/bin/env bash
set -euo pipefail

export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Repo root: $ROOT_DIR"

set -a
source .env
set +a

echo "==> Using DB container: climate_db"
echo "==> Checking processed files..."

CO2_CSV="$ROOT_DIR/data/processed/global_co2_yearly.csv"
TEMP_CSV="$ROOT_DIR/data/processed/global_temp_anomaly_yearly.csv"

if [[ ! -f "$CO2_CSV" ]]; then
  echo "ERROR: Missing $CO2_CSV"
  exit 1
fi
if [[ ! -f "$TEMP_CSV" ]]; then
  echo "ERROR: Missing $TEMP_CSV"
  exit 1
fi

echo "==> Processed files found."
echo "==> Truncating tables..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "TRUNCATE fact_global_co2_yearly, fact_global_temp_anomaly_yearly;"

echo "==> Copying CSVs into container..."

# Convert Git Bash paths (/c/...) to Windows paths (C:\...) for docker cp
CO2_WIN="$(cygpath -w "$CO2_CSV")"
TEMP_WIN="$(cygpath -w "$TEMP_CSV")"

docker cp "$CO2_WIN" climate_db:/tmp/global_co2_yearly.csv
docker cp "$TEMP_WIN" climate_db:/tmp/global_temp_anomaly_yearly.csv

echo "==> Loading CO2..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "\copy fact_global_co2_yearly FROM '/tmp/global_co2_yearly.csv' CSV HEADER"

echo "==> Loading TEMP..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "\copy fact_global_temp_anomaly_yearly FROM '/tmp/global_temp_anomaly_yearly.csv' CSV HEADER"

echo "==> Validating counts..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "SELECT COUNT(*) AS co2_rows FROM fact_global_co2_yearly;"

docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "SELECT COUNT(*) AS temp_rows FROM fact_global_temp_anomaly_yearly;"

echo "==> Validating year ranges..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM fact_global_co2_yearly;"

docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
  "SELECT MIN(year) AS min_year, MAX(year) AS max_year FROM fact_global_temp_anomaly_yearly;"

echo "==> Done."
