import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import UPLOADS_DIR, DATA_DIR, BASE_DIR
from backend.api import routes_health, routes_cyclones, routes_analysis, routes_datasets, routes_models
from backend.services.demo_service import init_demo_data

app = FastAPI(
    title="CycloneAI API",
    description="AI-Based Tropical Cyclone Identification, Classification and Prediction System",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folders for images and data downloads
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

# Register API Routers
app.include_router(routes_health.router, prefix="/api", tags=["Health"])
app.include_router(routes_cyclones.router, prefix="/api", tags=["Cyclones & Search"])
app.include_router(routes_analysis.router, prefix="/api", tags=["AI Analysis & Prediction"])
app.include_router(routes_datasets.router, prefix="/api", tags=["Datasets"])
app.include_router(routes_models.router, prefix="/api", tags=["Model Analytics"])

@app.on_event("startup")
def startup_event():
    # Initialize demo scenario and database if not already loaded
    try:
        init_demo_data()
    except Exception as e:
        print(f"Warning during startup demo data init: {e}")

@app.get("/")
def root():
    return {
        "title": "CycloneAI — Tropical Cyclone Intelligence System",
        "status": "Online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "disclaimer": "Research prototype for cyclone analysis. Forecast outputs must not replace official meteorological warnings."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
