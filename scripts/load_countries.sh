#!/usr/bin/env bash
set -euo pipefail

export MSYS_NO_PATHCONV=1
export MSYS2_ARG_CONV_EXCL="*"

# repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

set -a
source .env
set +a

GEOJSON="$ROOT_DIR/data/raw/countries.geojson"
if [[ ! -f "$GEOJSON" ]]; then
  echo "ERROR: Missing $GEOJSON"
  exit 1
fi

# Convert to Windows path for mounting on Git Bash
GEOJSON_WIN="$(cygpath -w "$GEOJSON")"

echo "==> Clearing dim_country..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "TRUNCATE dim_country CASCADE;"

echo "==> Loading dim_country via ogr2ogr (GeoJSON -> PostGIS)..."
# Use the compose network so the container can reach 'db' hostname
NET="$(docker inspect climate_db --format='{{range $k,$v := .NetworkSettings.Networks}}{{printf "%s" $k}}{{end}}')"

docker run --rm \
  --network "$NET" \
  -v "$GEOJSON_WIN":/data/countries.geojson \
  ghcr.io/osgeo/gdal:alpine-small-latest \
  ogr2ogr -f "PostgreSQL" -overwrite \
    PG:"host=db port=5432 dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD" \
    /data/countries.geojson \
    -nln dim_country \
    -lco GEOMETRY_NAME=geom \
    -nlt MULTIPOLYGON \
    -t_srs EPSG:4326 \
    -sql "SELECT NAME AS name, \"ISO3166-1-Alpha-3\" AS iso3
      FROM ne_10m_admin_0_countries
      WHERE \"ISO3166-1-Alpha-3\" IS NOT NULL
        AND \"ISO3166-1-Alpha-3\" LIKE '___'
        AND \"ISO3166-1-Alpha-3\" <> '-99'"

SIMPLIFY_TOLERANCE="${SIMPLIFY_TOLERANCE:-0.05}"
echo "==> Building dim_country.geom_simplified (tolerance=${SIMPLIFY_TOLERANCE})..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
  ALTER TABLE dim_country
    ADD COLUMN IF NOT EXISTS geom_simplified GEOMETRY(MULTIPOLYGON, 4326);
  UPDATE dim_country
     SET geom_simplified = ST_Multi(ST_SimplifyPreserveTopology(geom, ${SIMPLIFY_TOLERANCE}))
   WHERE geom IS NOT NULL;
  CREATE INDEX IF NOT EXISTS idx_dim_country_geom_simplified
    ON dim_country
    USING GIST (geom_simplified);
"



echo "==> Verifying dim_country..."
docker exec -i climate_db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) AS country_rows FROM dim_country;"
