CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS fact_global_co2_yearly (
  year INT PRIMARY KEY,
  co2_total_mt NUMERIC,
  co2_cumulative_mt NUMERIC
);

CREATE TABLE IF NOT EXISTS fact_global_temp_anomaly_yearly (
  year INT PRIMARY KEY,
  temp_anomaly_c NUMERIC,
  temp_uncertainty_c NUMERIC
);