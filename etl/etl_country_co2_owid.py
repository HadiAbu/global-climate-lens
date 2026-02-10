import pandas as pd
from pathlib import Path

# Paths
RAW_URL = "https://owid-public.owid.io/data/co2/owid-co2-data.csv"
OUT_PATH = Path("data/processed/country_co2_yearly.csv")

# Load
df = pd.read_csv(RAW_URL)

# ---- FILTERING ----
# ISO3 only (drops OWID_WRL, OWID_EUR, etc.)
df = df[df["iso_code"].str.len() == 3]

# Year bounds
df = df[(df["year"] >= 1750) & (df["year"] <= 2020)]

# ---- SELECT + RENAME ----
df = df[["iso_code", "year", "co2", "co2_per_capita"]]

df = df.rename(columns={"iso_code": "iso3", "co2": "co2_total_mt"})

# ---- SORT (deterministic output) ----
df = df.sort_values(["iso3", "year"])

# ---- WRITE ----
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("✅ Processed file written:", OUT_PATH)
print("Rows:", len(df))
print("ISO3 count:", df["iso3"].nunique())
print("Year range:", df["year"].min(), "-", df["year"].max())
