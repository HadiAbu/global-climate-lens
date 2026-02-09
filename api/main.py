from fastapi import FastAPI
import os

app = FastAPI(title="Global Climate Lens API")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "database_url_set": bool(os.getenv("DATABASE_URL")),
    }