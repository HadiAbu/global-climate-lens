from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import get_engine
from app.routers.spatial import router as spatial_router

app = FastAPI(title="Global Climate Lens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(spatial_router)


@app.get("/health")
def health():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/global/co2")
def global_co2():
    engine = get_engine()
    q = text(
        """
        SELECT year, co2_total_mt, co2_cumulative_mt
        FROM fact_global_co2_yearly
        ORDER BY year
    """
    )
    with engine.connect() as conn:
        return conn.execute(q).mappings().all()


@app.get("/global/temperature")
def global_temperature():
    engine = get_engine()
    q = text(
        """
        SELECT year, temp_anomaly_c, temp_uncertainty_c
        FROM fact_global_temp_anomaly_yearly
        ORDER BY year
    """
    )
    with engine.connect() as conn:
        return conn.execute(q).mappings().all()
