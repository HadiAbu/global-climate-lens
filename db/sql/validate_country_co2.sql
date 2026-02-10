-- scripts/validate_country_co2.sql

-- 1) Row count should be large (tens of thousands)
SELECT COUNT(*) AS fact_rows
FROM fact_country_co2_yearly;

-- 2) Orphan check (MUST be 0)
SELECT COUNT(*) AS orphan_rows
FROM fact_country_co2_yearly f
LEFT JOIN dim_country d ON d.iso3 = f.iso3
WHERE d.iso3 IS NULL;

-- 3) Quick sanity sample
SELECT *
FROM fact_country_co2_yearly
WHERE iso3 IN ('USA','CHN','IND','DEU')
ORDER BY iso3, year
LIMIT 40;
