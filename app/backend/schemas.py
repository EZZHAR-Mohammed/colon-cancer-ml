"""
schemas.py — Pydantic request/response models
"""

from pydantic import BaseModel
from typing import Dict


class PredictRequest(BaseModel):
    """
    Dynamic gene expression values.
    Keys are gene names, values are float expression levels.
    Example:
        { "Gene_54": 0.22, "Gene_781": -1.4, ... }
    """
    genes: Dict[str, float]


class PredictResponse(BaseModel):
    prediction: str
    confidence: float


class GenesResponse(BaseModel):
    selected_genes: list[str]


class HealthResponse(BaseModel):
    status: str


class RootResponse(BaseModel):
    message: str
