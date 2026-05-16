"""
Colon Cancer Gene Expression — Training Script
================================================
Workflow:
  1. Load dataset
  2. Encode labels, Scale full dataset
  3. Forward Feature Selection (10 steps) → Top 10 genes
  4. Use Top 6 genes → train / test split → final model
  5. Save model.pkl, scaler.pkl, selected_genes.json
"""

import os
import json
import time
import warnings

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

warnings.filterwarnings("ignore")

# ─── Paths ────────────────────────────────────────────────────────────────────
DATA_PATH   = "/app/data/colon_cancer_dataset.csv"
MODEL_DIR   = "/app/model"
MODEL_PATH  = os.path.join(MODEL_DIR, "model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
GENES_PATH  = os.path.join(MODEL_DIR, "selected_genes.json")

N_SELECT    = 10   # Forward Feature Selection steps
N_FINAL     = 6    # Genes used for the deployed model

os.makedirs(MODEL_DIR, exist_ok=True)


# ─── 1. Load Dataset ──────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  COLON CANCER ML — TRAINING PIPELINE")
print("="*60)

print(f"\n[1/6] Loading dataset from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"      Shape: {df.shape}  |  Columns: {list(df.columns[:5])} ... '{df.columns[-1]}'")

# ─── 2. Separate X / y ────────────────────────────────────────────────────────
X = df.drop("Class", axis=1)
y = df["Class"]
gene_names = list(X.columns)
print(f"      Features: {len(gene_names)}  |  Samples: {len(y)}")
print(f"      Classes: {y.unique().tolist()}")

# ─── 3. Encode Labels ─────────────────────────────────────────────────────────
print("\n[2/6] Encoding labels ...")
le = LabelEncoder()
y_enc = le.fit_transform(y)
print(f"      Mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# ─── 4. Standardise FULL dataset ──────────────────────────────────────────────
print("\n[3/6] Standardising full dataset (for feature selection) ...")
global_scaler = StandardScaler()
X_scaled = global_scaler.fit_transform(X)
print("      Done.")

# ─── 5. Forward Feature Selection ─────────────────────────────────────────────
print(f"\n[4/6] Forward Feature Selection — {N_SELECT} steps")
print("-"*60)

selected_indices  = []
selected_genes    = []
global_accuracies = []
remaining_indices = list(range(X_scaled.shape[1]))

clf_ffs = LogisticRegression(max_iter=1000, solver="lbfgs", random_state=42)

start = time.time()
for step in range(N_SELECT):
    best_acc   = -1
    best_idx   = None

    for idx in remaining_indices:
        candidate = selected_indices + [idx]
        X_candidate = X_scaled[:, candidate]
        clf_ffs.fit(X_candidate, y_enc)
        acc = accuracy_score(y_enc, clf_ffs.predict(X_candidate))
        if acc > best_acc:
            best_acc = acc
            best_idx = idx

    selected_indices.append(best_idx)
    remaining_indices.remove(best_idx)
    selected_genes.append(gene_names[best_idx])
    global_accuracies.append(best_acc)

    elapsed = time.time() - start
    print(f"  Step {step+1:>2}/{N_SELECT}  |  Gene: {gene_names[best_idx]:<20}  "
          f"|  Accuracy: {best_acc:.4f}  |  Elapsed: {elapsed:.1f}s")

print("-"*60)
print(f"  Top {N_SELECT} selected genes: {selected_genes}")

# ─── 6. Final Model with Top 6 ────────────────────────────────────────────────
print(f"\n[5/6] Building final model with Top {N_FINAL} genes ...")

final_genes   = selected_genes[:N_FINAL]
final_indices = selected_indices[:N_FINAL]
print(f"      Final genes: {final_genes}")

X_final = X[final_genes].values

X_train, X_test, y_train, y_test = train_test_split(
    X_final, y_enc,
    test_size=0.2,
    random_state=42,
    stratify=y_enc
)
print(f"      Train: {X_train.shape}  |  Test: {X_test.shape}")

# Fit scaler ONLY on training set
final_scaler = StandardScaler()
X_train_sc   = final_scaler.fit_transform(X_train)
X_test_sc    = final_scaler.transform(X_test)

# Train final model
clf_final = LogisticRegression(max_iter=1000, solver="lbfgs", random_state=42)
clf_final.fit(X_train_sc, y_train)

# Evaluation
train_acc = accuracy_score(y_train, clf_final.predict(X_train_sc))
test_acc  = accuracy_score(y_test,  clf_final.predict(X_test_sc))

print(f"\n      ── Evaluation ──")
print(f"      Train Accuracy : {train_acc:.4f}")
print(f"      Test  Accuracy : {test_acc:.4f}")
print(f"\n      Classification Report:")
target_names = le.inverse_transform([0, 1])
print(classification_report(y_test, clf_final.predict(X_test_sc),
                             target_names=target_names))
print(f"      Confusion Matrix:")
cm = confusion_matrix(y_test, clf_final.predict(X_test_sc))
print(f"      {cm}")

# ─── 7. Save Artefacts ────────────────────────────────────────────────────────
print(f"\n[6/6] Saving artefacts to: {MODEL_DIR}")

joblib.dump(clf_final,    MODEL_PATH)
joblib.dump(final_scaler, SCALER_PATH)

with open(GENES_PATH, "w") as f:
    json.dump(final_genes, f, indent=2)

print(f"      ✓ model.pkl          saved")
print(f"      ✓ scaler.pkl         saved")
print(f"      ✓ selected_genes.json saved  →  {final_genes}")

print("\n" + "="*60)
print("  TRAINING COMPLETE ✓")
print("="*60 + "\n")
