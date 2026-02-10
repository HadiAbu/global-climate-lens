from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from db import get_session

router = APIRouter(prefix="/spatial", tags=["spatial"])

ALLOWED_METRICS = {"co2_total_mt", "co2_per_capita"}
DEFAULT_SIMPLIFY_TOLERANCE = 0.05
DEFAULT_GEOJSON_PRECISION = 5


@router.get("/map/countries")
def map_countries(
    year: int = Query(..., ge=1750, le=2020),
    metric: str = Query("co2_total_mt"),
    limit_geometry: bool = Query(
        True,
        description="If true, return simplified country geometry to reduce payload size.",
    ),
    simplify_tolerance: float = Query(
        DEFAULT_SIMPLIFY_TOLERANCE,
        ge=0.0,
        le=1.0,
        description="Simplification tolerance in degrees for EPSG:4326 geometry.",
    ),
    db: Session = Depends(get_session),
):
    if metric not in ALLOWED_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric. Use one of: {sorted(ALLOWED_METRICS)}",
        )

    has_simplified_column = db.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'dim_country'
                  AND column_name = 'geom_simplified'
            )
            """
        )
    ).scalar_one()

    if limit_geometry:
        if has_simplified_column:
            geom_expr = (
                "COALESCE(d.geom_simplified, "
                "ST_SimplifyPreserveTopology(d.geom, :simplify_tolerance))"
            )
        else:
            geom_expr = "ST_SimplifyPreserveTopology(d.geom, :simplify_tolerance)"
    else:
        geom_expr = "d.geom"

    sql = text(
        f"""
        SELECT
            d.iso3,
            d.name,
            f.{metric} AS value,
            ST_AsGeoJSON(
                ST_Multi({geom_expr}),
                :geojson_precision
            )::json AS geometry
        FROM dim_country d
        JOIN fact_country_co2_yearly f
          ON f.iso3 = d.iso3
        WHERE f.year = :year
        """
    )

    params = {"year": year, "geojson_precision": DEFAULT_GEOJSON_PRECISION}
    if limit_geometry:
        params["simplify_tolerance"] = simplify_tolerance

    rows = db.execute(sql, params).mappings().all()

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": r["geometry"],
                "properties": {
                    "iso3": r["iso3"],
                    "name": r["name"],
                    "value": r["value"],
                    "year": year,
                    "metric": metric,
                },
            }
            for r in rows
        ],
    }


@router.get("/country/{iso3}/co2")
def country_co2_timeseries(
    iso3: str,
    db: Session = Depends(get_session),
):
    iso3 = iso3.upper()

    exists = db.execute(
        text("SELECT 1 FROM dim_country WHERE iso3 = :iso3"),
        {"iso3": iso3},
    ).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Unknown ISO3")

    rows = (
        db.execute(
            text(
                """
            SELECT year, co2_total_mt, co2_per_capita
            FROM fact_country_co2_yearly
            WHERE iso3 = :iso3
            ORDER BY year
            """
            ),
            {"iso3": iso3},
        )
        .mappings()
        .all()
    )

    return {"iso3": iso3, "series": list(rows)}
