🌍 Project Specification
Global Climate Lens — CO₂ Emissions & Temperature Anomalies (1750–2020)

Anchor domain: Environment
Optimization goal: Hiring (software + data + geospatial)
Target roles: Geospatial Data amalg Engineer / Environmental Data Scientist / GIS Software Engineer
Relocation-ready: Yes (global datasets, standard stack)

1. Project Goal

Build an end-to-end geospatial analytics platform that:

Analyzes long-run global CO₂ emissions and temperature anomalies

Provides interactive exploration via charts and maps

Combines global climate context with country-level spatial emissions

Demonstrates real production thinking: ETL → DB → API → Web UI

This is not a map demo.
It is a data product.

2. Core Question the Project Answers

How has cumulative global CO₂ evolved since 1750, how does it relate to temperature anomalies, and how do individual countries contribute to the global emissions trajectory over time?


3. Data Sources (Frozen)
3.1 Primary (Kaggle — Global, Non-Spatial)

Dataset:
lucalullo/global-co2-climate-data-1750-2020

File A — Global CO₂ emissions

Rows: 271 (1750–2020)

Columns:

anno → year

emissioni CO₂ totali (Mt/anno) → co2_total_mt

emissioni CO₂ cumulate totali (Mt) → co2_cumulative_mt

No missing values

File B — Global temperature anomalies

Rows: 271

Columns:

anno → year

anomalia annuale reale → temp_anomaly_c

margine di errore (± °C) → temp_uncertainty_c

Missing values exist (e.g. early years)

📌 Important
These datasets are GLOBAL ONLY (no country, no geometry).
They serve as contextual climate indicators, not map layers.

3.2 Spatial Enrichment (Required for GIS)

To introduce spatial resolution:

Country geometries

Natural Earth Admin 0

Geometry: MULTIPOLYGON

Identifier: ISO3

Country-level CO₂ emissions (yearly)

OWID-style country emissions dataset

Metrics:

Total CO₂ (Mt)

CO₂ per capita

Yearly grain

ISO3-aligned

📌 These datasets are conceptually consistent with Kaggle’s source lineage (OWID + Berkeley Earth).

4. Final Data Model (Locked)
4.1 Dimension Tables
dim_country
column	type	notes
iso3	TEXT (PK)	ISO 3166-1 alpha-3
name	TEXT	country name
geom	GEOMETRY(MULTIPOLYGON, 4326)	spatial
continent	TEXT	optional
income_group	TEXT	optional
dim_year
column	type
year	INT (PK)
4.2 Fact Tables
fact_global_co2_yearly
column	type
year	INT (PK)
co2_total_mt	NUMERIC
co2_cumulative_mt	NUMERIC
fact_global_temp_anomaly_yearly
column	type
year	INT (PK)
temp_anomaly_c	NUMERIC
temp_uncertainty_c	NUMERIC
fact_country_co2_yearly
column	type
iso3	TEXT (FK → dim_country)
year	INT (FK → dim_year)
co2_total_mt	NUMERIC
co2_per_capita	NUMERIC
PK	(iso3, year)
4.3 Indexing Strategy

GIST(dim_country.geom)

BTREE(fact_country_co2_yearly.iso3, year)

BTREE(fact_global_*_yearly.year)

This supports:

Fast choropleth queries

Time-series scans

Drill-down performance

5. System Architecture
[ Kaggle / External CSVs ]
            ↓
      [ ETL (Python) ]
            ↓
      [ Postgres + PostGIS ]
            ↓
       [ FastAPI API ]
            ↓
[ React + Web Map + Charts ]


Fully reproducible via Docker Compose.

6. ETL Design (Deterministic)
ETL Responsibilities

Ingest raw CSVs

Rename columns → English

Normalize years and numeric types

Handle missing temperature values:

Keep NULLs

Do not interpolate (document explicitly)

Load into PostGIS with indexes

ETL Structure
etl/
  01_ingest_global.py
  02_ingest_country.py
  03_ingest_geometry.py
  validate.py

7. API Contract (Frozen)
Global
GET /global/co2
→ [{ year, co2_total_mt, co2_cumulative_mt }]

GET /global/temperature
→ [{ year, temp_anomaly_c, temp_uncertainty_c }]

Map
GET /map/countries?year=YYYY&metric=co2|co2_per_capita
→ GeoJSON

Drill-down
GET /country/{iso3}/co2
→ [{ year, co2_total_mt, co2_per_capita }]


API is:

Stateless

Frontend-agnostic

Pagination-ready

8. Frontend UX Specification
Layout

Top panel:
Global CO₂ + temperature anomaly (dual line chart, shared x-axis)

Main panel:
Choropleth world map

Metric toggle

Year slider

Tooltip on hover

Click to select country

Detail panel:
Country CO₂ time series vs global reference

UX Quality Signals

Skeleton loaders

Debounced year slider

URL state (?year=1990&metric=co2_per_capita&country=DEU)

9. What the Map Shows (Scientifically Correct)

✅ Country CO₂ emissions
❌ Country temperature anomalies (not scientifically valid at this resolution)

Global temperature is context, not a map layer.

10. Technology Stack (Final)

ETL: Python, pandas, GeoPandas

DB: PostgreSQL + PostGIS

API: FastAPI

Frontend: React + Leaflet/Mapbox + Recharts

Infra: Docker Compose

11. Explicit Non-Goals (Scope Control)

No authentication

No streaming

No ML forecasting

No microservices

No mobile-first work