GLOBAL CLIMATE LENS - DATA HANDBOOK (MILESTONE 3)
Snapshot date: February 10, 2026
Environment: local Postgres/PostGIS loaded by current ETL and scripts in this repo

====================================================================
1) PURPOSE
====================================================================
This document explains:
- how to work with the data model in this repository
- what can be reliably derived from the current loaded data
- major anomalies and caveats discovered during profiling
- reproducible SQL to verify findings and build new analyses

This is an operational guide, not a climate policy report.

====================================================================
2) DATA INVENTORY (CURRENT SNAPSHOT)
====================================================================
Core tables and row counts:
- fact_global_co2_yearly: 271 rows
- fact_global_temp_anomaly_yearly: 271 rows
- fact_country_co2_yearly: 40,784 rows
- dim_country: 236 rows

Year ranges:
- global CO2: 1750..2020
- global temperature: 1750..2020
- country CO2: 1750..2020

Primary keys and joins:
- fact_global_co2_yearly(year)
- fact_global_temp_anomaly_yearly(year)
- fact_country_co2_yearly(iso3, year)
- dim_country(iso3)

Main join paths:
- global series: fact_global_co2_yearly JOIN fact_global_temp_anomaly_yearly USING(year)
- map/drilldown: fact_country_co2_yearly JOIN dim_country ON iso3

====================================================================
3) HOW THE PIPELINE WORKS
====================================================================
Files that define behavior:
- etl/01_global_etl.py
- etl/02_ingest_country.py
- etl/03_load_country_co2.py
- scripts/load_global.sh
- scripts/load_countries.sh
- scripts/validate_country_co2.py

Key behavior by stage:
1. Global ETL
   - renames source columns to English fields
   - keeps years in [1750, 2020]
   - keeps temperature nulls as null (no interpolation)

2. Country ingest
   - pulls OWID CO2 CSV
   - keeps ISO3-like codes (len == 3)
   - keeps years in [1750, 2020]
   - selects: iso3, year, co2_total_mt, co2_per_capita

3. Country load
   - creates fact table and FK to dim_country
   - filters country rows to iso3 present in dim_country
   - truncates/reloads fact_country_co2_yearly

4. Spatial load
   - loads Natural Earth geometry into dim_country
   - excludes ISO -99 and malformed values
   - optional simplified geometry generation exists in scripts/schema,
     but current runtime DB snapshot does not yet contain geom_simplified

====================================================================
4) HOW TO WORK WITH THIS DATA SAFELY
====================================================================
Recommended practices:
- Always report coverage counts with each chart:
  countries_with_total, countries_with_per_capita, and null counts.
- Treat null and zero as different states.
- For per-capita ranking, use percentile filtering or robust scales.
- For long-run trends, segment early (high uncertainty/sparse coverage)
  and modern periods.
- For map analyses, expect country-sum totals to be below global totals.

Do not:
- assume country sum equals global total
- assume all major ISO3 are present in geometry
- fill missing values silently with zero
- compare early and modern periods without uncertainty context

====================================================================
5) DATA QUALITY PROFILE (MEASURED)
====================================================================
Global completeness:
- co2_total_mt nulls: 0
- co2_cumulative_mt nulls: 0
- temp_anomaly_c nulls: 1
- temp_uncertainty_c nulls: 1
- missing global temp year: 1752 only

Global consistency:
- cumulative monotonic violations: 0

Country completeness:
- co2_total_mt null rows: 18,856
- co2_per_capita null rows: 19,201
- total null + per-capita present rows: 0
- total present + per-capita null rows: 345

Countries with all-null totals:
- MCO (Monaco)
- SMR (San Marino)
- VAT (Vatican)

Referential integrity:
- orphan rows in fact_country_co2_yearly: 0

Coverage growth by year (country total non-null):
- first year with >= 50 countries: 1870
- first year with >= 100 countries: 1933
- first year with >= 150 countries: 1950
- first year with >= 200 countries: 1990
- 2020: 211 countries with non-null totals

====================================================================
6) HIGH-IMPACT ANOMALIES
====================================================================
ANOMALY A: Missing important ISO3 in geometry dimension
- Processed country file has 218 iso3 values
- Only 214 iso3 remain after filtering to dim_country
- Missing from dim_country: FRA, NOR, BES, CXR
- Dropped rows: 824
- 2020 dropped CO2 total: about 322.92 Mt (about 0.94% of country-sum 2020)
- All-years dropped CO2 total: about 41,551 Mt

Interpretation:
- Map and country analyses understate totals where these ISO3 matter.
- This is a geometry/ISO harmonization issue, not an API math issue.

ANOMALY B: Source geometry contains no FRA/NOR ISO3 in current raw file
- data/raw/countries.geojson:
  - feature_count: 258
  - unique_iso3: 237
  - contains_FRA: false
  - contains_NOR: false
  - "-99" appears 22 times in source

ANOMALY C: Extreme historical per-capita outliers
- Top all-time per-capita values include very high small-territory spikes:
  - SXM 1954: 782.74
  - SXM 1956: 741.27
  - KWT 1991: 364.79
- Rows with co2_per_capita > 100: 36 (mostly SXM)

Interpretation:
- Per-capita plots need log scale, clipping, or separate outlier handling.

ANOMALY D: Country year gaps
- Several countries have discontinuous year rows (example):
  - BEL gap 1802 -> 1830 (28 years)
  - many codes with 1833 -> 1850 gap (17 years)

Interpretation:
- Time-series models must not assume yearly continuity per country.

====================================================================
7) INSIGHTFUL DISCOVERIES FROM CURRENT DATA
====================================================================
GLOBAL SIGNALS
- Warmest year in series: 2020 (temp anomaly 1.513 C)
- First year with temp anomaly >= 1.0 C: 2005
- Largest global annual CO2 increase: 2010 (+1804.7 Mt)
- Largest global annual CO2 decrease: 2020 (-1928.4 Mt)

DECADE SHIFT
- Avg global CO2 total:
  - 2001-2010: 29,679.4 Mt
  - 2011-2020: 35,592.6 Mt
  - delta: +5,913.2 Mt
- Avg temp anomaly:
  - 2001-2010: 0.948 C
  - 2011-2020: 1.179 C
  - delta: +0.231 C

CUMULATIVE CONCENTRATION IN MODERN ERA
Share of 2020 cumulative reached by:
- 1900: 2.66%
- 1950: 13.66%
- 1980: 35.49%
- 2000: 61.56%
- 2020: 100%

GLOBAL-COUNTRY RECONCILIATION
- Sum(country totals over all years): 1,614,572 Mt
- Global cumulative 2020: 1,698,036.6 Mt
- Country sum as % of global cumulative: 95.08%
- Gap: 83,464.41 Mt

Interpretation:
- Country table is close but not fully exhaustive vs global total.
- Gap is expected given territories/bunker differences and missing iso3 in geometry.

LEADERSHIP AND CONCENTRATION
- Top emitter by milestone:
  - 1850: GBR
  - 1900: USA
  - 1950: USA
  - 1980: USA
  - 2000: USA
  - 2020: CHN
- First year CHN > USA: 2006
- 2020 country-sum shares:
  - CHN: 32.06%
  - USA: 13.80%
  - IND: 7.13%

Concentration (country-sum basis):
- 2020 top1 share: 32.06%
- 2020 top3 share: 52.99%
- 2020 top10 share: 70.45%

Long-run cumulative concentration:
- Top1 country cumulative share: 25.70%
- Top3 cumulative share: 47.60%
- Top10 cumulative share: 71.34%
- Top20 cumulative share: 82.69%

CORRELATION NOTE (DESCRIPTIVE, NOT CAUSAL)
- corr(global co2 total, temp anomaly same year): 0.7836
- corr(global co2 total, temp anomaly +10y): 0.7990
- corr(global co2 total, temp anomaly +20y): 0.8194

====================================================================
8) MAP / API PERFORMANCE OBSERVATIONS
====================================================================
Endpoint:
- /spatial/map/countries?year=2020&metric=co2_total_mt

Payload size from current API settings:
- limit_geometry=true: 1,341,071 bytes
- limit_geometry=false: 10,789,617 bytes
- reduction: 87.57%

Conclusion:
- Simplified geometry mode is materially better for UI response time
  and browser rendering.

====================================================================
9) REPRODUCIBLE SQL SNIPPETS
====================================================================
All snippets target current schema names in this repo.

9.1 Core row counts and year ranges
SELECT COUNT(*) FROM fact_global_co2_yearly;
SELECT COUNT(*) FROM fact_global_temp_anomaly_yearly;
SELECT COUNT(*) FROM fact_country_co2_yearly;
SELECT COUNT(*) FROM dim_country;

SELECT MIN(year), MAX(year) FROM fact_global_co2_yearly;
SELECT MIN(year), MAX(year) FROM fact_global_temp_anomaly_yearly;
SELECT MIN(year), MAX(year) FROM fact_country_co2_yearly;

9.2 Global null profile
SELECT
  SUM(CASE WHEN co2_total_mt IS NULL THEN 1 ELSE 0 END) AS co2_total_nulls,
  SUM(CASE WHEN co2_cumulative_mt IS NULL THEN 1 ELSE 0 END) AS co2_cumulative_nulls
FROM fact_global_co2_yearly;

SELECT
  SUM(CASE WHEN temp_anomaly_c IS NULL THEN 1 ELSE 0 END) AS temp_anomaly_nulls,
  SUM(CASE WHEN temp_uncertainty_c IS NULL THEN 1 ELSE 0 END) AS temp_uncertainty_nulls
FROM fact_global_temp_anomaly_yearly;

SELECT year, temp_anomaly_c, temp_uncertainty_c
FROM fact_global_temp_anomaly_yearly
WHERE temp_anomaly_c IS NULL OR temp_uncertainty_c IS NULL
ORDER BY year;

9.3 Global cumulative monotonic check
SELECT COUNT(*) AS violations
FROM (
  SELECT year, co2_cumulative_mt,
         LAG(co2_cumulative_mt) OVER (ORDER BY year) AS prev
  FROM fact_global_co2_yearly
) s
WHERE prev IS NOT NULL AND co2_cumulative_mt < prev;

9.4 Global YOY extremes
SELECT year, co2_total_mt - LAG(co2_total_mt) OVER (ORDER BY year) AS yoy_change
FROM fact_global_co2_yearly
ORDER BY yoy_change DESC NULLS LAST
LIMIT 10;

SELECT year, co2_total_mt - LAG(co2_total_mt) OVER (ORDER BY year) AS yoy_change
FROM fact_global_co2_yearly
ORDER BY yoy_change ASC NULLS LAST
LIMIT 10;

9.5 Decade averages and recent decade delta
SELECT (year/10)*10 AS decade,
       AVG(co2_total_mt) AS avg_co2_total_mt,
       AVG(temp_anomaly_c) AS avg_temp_anomaly_c,
       AVG(temp_uncertainty_c) AS avg_temp_uncertainty_c
FROM fact_global_co2_yearly g
JOIN fact_global_temp_anomaly_yearly t USING(year)
GROUP BY (year/10)*10
ORDER BY decade;

WITH y AS (
  SELECT year, co2_total_mt, temp_anomaly_c
  FROM fact_global_co2_yearly g
  JOIN fact_global_temp_anomaly_yearly t USING(year)
),
a AS (
  SELECT
    AVG(co2_total_mt) FILTER (WHERE year BETWEEN 2011 AND 2020) AS co2_2011_2020,
    AVG(co2_total_mt) FILTER (WHERE year BETWEEN 2001 AND 2010) AS co2_2001_2010,
    AVG(temp_anomaly_c) FILTER (WHERE year BETWEEN 2011 AND 2020) AS temp_2011_2020,
    AVG(temp_anomaly_c) FILTER (WHERE year BETWEEN 2001 AND 2010) AS temp_2001_2010
  FROM y
)
SELECT
  co2_2011_2020, co2_2001_2010, (co2_2011_2020 - co2_2001_2010) AS co2_delta,
  temp_2011_2020, temp_2001_2010, (temp_2011_2020 - temp_2001_2010) AS temp_delta
FROM a;

9.6 Country null profile and integrity
SELECT
  SUM(CASE WHEN co2_total_mt IS NULL THEN 1 ELSE 0 END) AS co2_total_nulls,
  SUM(CASE WHEN co2_per_capita IS NULL THEN 1 ELSE 0 END) AS co2_per_capita_nulls,
  SUM(CASE WHEN co2_total_mt IS NULL AND co2_per_capita IS NOT NULL THEN 1 ELSE 0 END) AS total_null_percap_present,
  SUM(CASE WHEN co2_total_mt IS NOT NULL AND co2_per_capita IS NULL THEN 1 ELSE 0 END) AS total_present_percap_null
FROM fact_country_co2_yearly;

SELECT COUNT(*) AS orphan_rows
FROM fact_country_co2_yearly f
LEFT JOIN dim_country d ON d.iso3 = f.iso3
WHERE d.iso3 IS NULL;

9.7 Coverage by year
SELECT year,
       COUNT(*) FILTER (WHERE co2_total_mt IS NOT NULL) AS countries_with_total,
       COUNT(*) FILTER (WHERE co2_per_capita IS NOT NULL) AS countries_with_per_capita
FROM fact_country_co2_yearly
GROUP BY year
ORDER BY year;

9.8 Top emitters and per-capita leaders (2020)
SELECT f.iso3, d.name, f.co2_total_mt
FROM fact_country_co2_yearly f
JOIN dim_country d ON d.iso3 = f.iso3
WHERE f.year = 2020 AND f.co2_total_mt IS NOT NULL
ORDER BY f.co2_total_mt DESC
LIMIT 20;

SELECT f.iso3, d.name, f.co2_per_capita
FROM fact_country_co2_yearly f
JOIN dim_country d ON d.iso3 = f.iso3
WHERE f.year = 2020 AND f.co2_per_capita IS NOT NULL
ORDER BY f.co2_per_capita DESC
LIMIT 20;

9.9 Country concentration by year (top1/top3/top10 shares)
WITH y AS (
  SELECT year, iso3, co2_total_mt,
         SUM(co2_total_mt) OVER (PARTITION BY year) AS ysum,
         ROW_NUMBER() OVER (PARTITION BY year ORDER BY co2_total_mt DESC NULLS LAST) AS rn
  FROM fact_country_co2_yearly
  WHERE co2_total_mt IS NOT NULL
)
SELECT year,
       100.0 * SUM(CASE WHEN rn<=1  THEN co2_total_mt ELSE 0 END) / MAX(ysum) AS top1_share_pct,
       100.0 * SUM(CASE WHEN rn<=3  THEN co2_total_mt ELSE 0 END) / MAX(ysum) AS top3_share_pct,
       100.0 * SUM(CASE WHEN rn<=10 THEN co2_total_mt ELSE 0 END) / MAX(ysum) AS top10_share_pct
FROM y
GROUP BY year
ORDER BY year;

9.10 Country vs global reconciliation by year
SELECT g.year,
       g.co2_total_mt AS global_total,
       SUM(f.co2_total_mt) AS country_sum,
       (SUM(f.co2_total_mt) - g.co2_total_mt) AS diff,
       100.0 * SUM(f.co2_total_mt) / NULLIF(g.co2_total_mt,0) AS country_as_pct_of_global
FROM fact_global_co2_yearly g
LEFT JOIN fact_country_co2_yearly f ON f.year = g.year
GROUP BY g.year, g.co2_total_mt
ORDER BY g.year;

9.11 Missing ISO from processed artifact vs dim_country
-- Run outside DB using pandas from data/processed/country_co2_yearly.csv,
-- or load that CSV to temp table and compare:
-- SELECT DISTINCT iso3 FROM processed_country EXCEPT SELECT iso3 FROM dim_country;

====================================================================
10) ACTION PLAN TO IMPROVE DATA RELIABILITY
====================================================================
Priority 1:
- Fix geometry source/harmonization so FRA and NOR are present in dim_country.
- Re-run country load and re-check dropped ISO3 list.

Priority 2:
- Add a persistent QA report table/view with:
  - yearly coverage counts
  - missing expected major ISO3
  - per-capita extreme thresholds
  - country/global reconciliation bands

Priority 3:
- Add explicit iso3 mapping table for known exceptions and territories.
- Keep raw source metadata versioned (source date/hash).

Priority 4:
- Enable geom_simplified in runtime DB and validate point reduction.

====================================================================
11) SUMMARY
====================================================================
The dataset is analysis-ready for global trends and country-level mapping,
with solid referential integrity and good API behavior. The largest
structural risk is geometry ISO mismatch (notably FRA/NOR absent in dim_country),
plus expected long-tail sparsity and per-capita outliers in early/small
territory records. With ISO harmonization and standardized QA reporting,
this becomes a strong production-grade analytical dataset.

