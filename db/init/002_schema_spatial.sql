CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS dim_country (
  iso3 TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  continent TEXT,
  income_group TEXT,
  geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_country_co2_yearly (
  iso3 TEXT NOT NULL REFERENCES dim_country(iso3),
  year INT NOT NULL,
  co2_total_mt NUMERIC,
  co2_per_capita NUMERIC,
  PRIMARY KEY (iso3, year)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dim_country_geom ON dim_country USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_fact_country_year ON fact_country_co2_yearly (year);
