"""
main.py — FastAPI application
Frontend served at /  |  API at /api/*  |  Docs at /docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.schemas import (
    PredictRequest,
    PredictResponse,
    GenesResponse,
    HealthResponse,
    RootResponse,
)
from backend.predictor import predictor

import os

# backend/ is at /app/backend/ — go up one level to /app/ then into frontend/
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

# ─── App init ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Colon Cancer Prediction API",
    description="Gene expression-based colon cancer classifier — Logistic Regression + Forward Feature Selection",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── API Routes (/api/*) ──────────────────────────────────────────────────────

@app.get("/api", response_model=RootResponse, tags=["General"])
def api_root():
    """API welcome message."""
    return {"message": "Colon Cancer Prediction API"}


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health():
    """Liveness probe."""
    return {"status": "healthy"}


@app.get("/genes", response_model=GenesResponse, tags=["Model"])
def get_genes():
    """Return the 6 selected gene names used by the model."""
    return {"selected_genes": predictor.get_genes()}


@app.post("/predict", response_model=PredictResponse, tags=["Model"])
def predict(request: PredictRequest):
    """
    Predict Normal / Abnormal from gene expression values.

    Body example:
    ```json
    {
      "genes": {
        "M63391": 0.83,
        "T62947": -1.42
      }
    }
    ```
    """
    try:
        prediction, confidence = predictor.predict(request.genes)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"prediction": prediction, "confidence": confidence}


# ─── Static assets (CSS, JS) ──────────────────────────────────────────────────
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ─── Frontend — serve index.html for / and any unknown route ──────────────────
@app.get("/", include_in_schema=False)
def serve_root():
    """Serve the frontend SPA at the root URL."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/{full_path:path}", include_in_schema=False)
def catch_all(full_path: str):
    """Catch-all: serve index.html for unknown paths (SPA routing)."""
    # Guard: don't shadow real API routes
    api_prefixes = ("api", "health", "genes", "predict", "docs", "openapi", "static")
    if any(full_path.startswith(p) for p in api_prefixes):
        raise HTTPException(status_code=404)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
