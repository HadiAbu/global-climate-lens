from __future__ import annotations
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

CO2_FILE = RAW / "global-co2-emissions-historical-1750-2020.csv"
TEMP_FILE = RAW / "global-land-temperature-anomalies-1750-2020.csv"

OUT_CO2 = OUT / "global_co2_yearly.csv"
OUT_TEMP = OUT / "global_temp_anomaly_yearly.csv"


def _validate_years(df: pd.DataFrame, name: str) -> None:
    years = pd.to_numeric(df["year"], errors="coerce").dropna().astype(int)
    print(f"\n[{name}] shape: {df.shape}")
    print(f"[{name}] year min/max: {years.min()}..{years.max()}")
    print(f"[{name}] duplicate years: {df['year'].duplicated().sum()}")
    print(f"[{name}] missing values:\n{df.isna().sum()}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    if not CO2_FILE.exists():
        raise FileNotFoundError(f"Missing: {CO2_FILE}")
    if not TEMP_FILE.exists():
        raise FileNotFoundError(f"Missing: {TEMP_FILE}")

    df_co2_raw = pd.read_csv(CO2_FILE)
    df_tmp_raw = pd.read_csv(TEMP_FILE)

    # ---- CO2 clean ----
    df_co2 = df_co2_raw.rename(
        columns={
            "anno": "year",
            "emissioni CO₂ totali (Mt/anno)": "co2_total_mt",
            "emissioni CO₂ cumulate totali (Mt)": "co2_cumulative_mt",
        }
    ).copy()

    df_co2["year"] = pd.to_numeric(df_co2["year"], errors="coerce").astype("Int64")
    df_co2["co2_total_mt"] = pd.to_numeric(df_co2["co2_total_mt"], errors="coerce")
    df_co2["co2_cumulative_mt"] = pd.to_numeric(
        df_co2["co2_cumulative_mt"], errors="coerce"
    )

    # keep expected range
    df_co2 = df_co2[(df_co2["year"] >= 1750) & (df_co2["year"] <= 2020)].sort_values(
        "year"
    )

    # ---- TEMP clean ----
    df_tmp = df_tmp_raw.rename(
        columns={
            "anno": "year",
            "anomalia annuale reale": "temp_anomaly_c",
            "margine di errore (± °C)": "temp_uncertainty_c",
        }
    ).copy()

    df_tmp["year"] = pd.to_numeric(df_tmp["year"], errors="coerce").astype("Int64")
    df_tmp["temp_anomaly_c"] = pd.to_numeric(df_tmp["temp_anomaly_c"], errors="coerce")
    df_tmp["temp_uncertainty_c"] = pd.to_numeric(
        df_tmp["temp_uncertainty_c"], errors="coerce"
    )

    df_tmp = df_tmp[(df_tmp["year"] >= 1750) & (df_tmp["year"] <= 2020)].sort_values(
        "year"
    )

    # ---- validations ----
    _validate_years(df_co2, "CO2")
    _validate_years(df_tmp, "TEMP")

    if not df_co2["year"].is_unique:
        raise ValueError("CO2 table has duplicate years")
    if not df_tmp["year"].is_unique:
        raise ValueError("TEMP table has duplicate years")

    # Important: keep NaNs in temp anomaly as NULLs (no interpolation)
    df_co2.to_csv(OUT_CO2, index=False)
    df_tmp.to_csv(OUT_TEMP, index=False)

    print(f"\nWrote: {OUT_CO2}")
    print(f"Wrote: {OUT_TEMP}")


if __name__ == "__main__":
    main()
