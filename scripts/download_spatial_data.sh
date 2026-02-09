#!/usr/bin/env bash
set -euo pipefail

mkdir -p data/raw

# Official-ish GeoJSON packaging of Natural Earth Admin-0 countries (DataHub core dataset)
COUNTRIES_GEOJSON_URL="https://datahub.io/core/geo-countries/_r/-/data/countries.geojson"

# OWID complete CO2 dataset (official OWID public bucket)
OWID_CO2_URL="https://owid-public.owid.io/data/co2/owid-co2-data.csv"

echo "==> Downloading countries GeoJSON..."
curl -L "$COUNTRIES_GEOJSON_URL" -o data/raw/countries.geojson

echo "==> Downloading OWID CO2 dataset..."
curl -L "$OWID_CO2_URL" -o data/raw/owid-co2-data.csv

echo "==> Done."
ls -lh data/raw/countries.geojson data/raw/owid-co2-data.csv
