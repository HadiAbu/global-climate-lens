-- db/sql/04_fact_country_co2_yearly.sql
CREATE TABLE IF NOT EXISTS fact_country_co2_yearly (
  iso3 TEXT NOT NULL,
  year INT NOT NULL,
  co2_total_mt NUMERIC,
  co2_per_capita NUMERIC,
  PRIMARY KEY (iso3, year),
  CONSTRAINT fk_fact_country_co2_yearly_country
    FOREIGN KEY (iso3)
    REFERENCES dim_country (iso3)
);

-- Helpful index for time-series scans (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_fact_country_co2_yearly_year
  ON fact_country_co2_yearly (year);
