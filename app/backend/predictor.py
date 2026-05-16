"""
predictor.py — Model loading and inference logic
"""

import os
import json
from typing import Dict, Tuple

import numpy as np
import joblib


MODEL_DIR   = os.environ.get("MODEL_DIR", "/app/model")
MODEL_PATH  = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
GENES_PATH  = os.path.join(MODEL_DIR, "selected_genes.json")


class ColonCancerPredictor:
    """
    Loads trained artefacts and exposes a predict() method.
    All gene reordering and scaling is handled internally.
    """

    def __init__(self):
        print("[Predictor] Loading model artefacts ...")
        self.model          = joblib.load(MODEL_PATH)
        self.scaler         = joblib.load(SCALER_PATH)
        self.selected_genes = self._load_genes()
        print(f"[Predictor] Ready — genes: {self.selected_genes}")

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _load_genes() -> list:
        with open(GENES_PATH, "r") as f:
            return json.load(f)

    # ── Public API ───────────────────────────────────────────────────────────

    def get_genes(self) -> list:
        return self.selected_genes

    def predict(self, gene_values: Dict[str, float]) -> Tuple[str, float]:
        """
        Parameters
        ----------
        gene_values : dict  { gene_name: float_value, ... }

        Returns
        -------
        prediction  : "Normal" or "Abnormal"
        confidence  : probability of predicted class  (0–1)

        Raises
        ------
        ValueError if any required gene is missing from gene_values.
        """
        # 1. Validate — check for missing genes
        missing = [g for g in self.selected_genes if g not in gene_values]
        if missing:
            raise ValueError(f"Missing genes in request: {missing}")

        # 2. Reorder — exact order the model expects
        values = np.array(
            [gene_values[g] for g in self.selected_genes],
            dtype=np.float64
        ).reshape(1, -1)

        # 3. Scale
        values_scaled = self.scaler.transform(values)

        # 4. Predict
        pred_idx    = self.model.predict(values_scaled)[0]
        pred_proba  = self.model.predict_proba(values_scaled)[0]
        confidence  = float(pred_proba[pred_idx])

        # Map index → label  (1 = Abnormal, 0 = Normal based on LabelEncoder)
        label_map  = {0: "Normal", 1: "Abnormal"}
        prediction = label_map.get(int(pred_idx), str(pred_idx))

        return prediction, round(confidence, 4)


# Singleton — loaded once at startup
predictor = ColonCancerPredictor()
