-- Add and backfill a simplified geometry column for faster GeoJSON payloads.
-- Default tolerance 0.05 (degrees) keeps country shape while cutting vertex count.

ALTER TABLE dim_country
  ADD COLUMN IF NOT EXISTS geom_simplified GEOMETRY(MULTIPOLYGON, 4326);

UPDATE dim_country
SET geom_simplified = ST_Multi(ST_SimplifyPreserveTopology(geom, 0.05))
WHERE geom IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_dim_country_geom_simplified
  ON dim_country
  USING GIST (geom_simplified);
