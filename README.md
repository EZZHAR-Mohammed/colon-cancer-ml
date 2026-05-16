# 🧬 Colon Cancer Gene Expression Predictor

> A production-ready Machine Learning system for colon cancer classification using gene expression data, Forward Feature Selection, and Logistic Regression.

---

## 📋 Project Overview

| Property       | Detail                                              |
|----------------|-----------------------------------------------------|
| Dataset        | Colon cancer gene expression (62 patients, ~2000 genes) |
| Target         | `Normal` / `Abnormal`                               |
| Algorithm      | Logistic Regression                                 |
| Feature Method | Forward Feature Selection                           |
| Top genes      | 10 selected → 6 used for final model                |
| Backend        | FastAPI + uvicorn                                   |
| Frontend       | HTML + CSS + Vanilla JS                             |
| Container      | Docker + Docker Compose                             |

---


## 🚀 Quick Start

### Step 1 — Train the model

```bash
docker compose run training
```

This will:
- Load the dataset
- Standardise features
- Run Forward Feature Selection (10 steps)
- Train the final model on the top 6 genes
- Save `model.pkl`, `scaler.pkl`, `selected_genes.json` to `./model/`

---

### Step 2 — Start the application

```bash
docker compose up --build
```

---

### Step 3 — Open your browser

```
http://localhost:8000
```

---

## 🔬 Scientific Workflow

```
Dataset CSV (~2000 genes, 62 patients)
   │
   ▼
LabelEncoder  +  StandardScaler (full dataset)
   │
   ▼
Forward Feature Selection (10 iterations)
   │  → At each step: try all remaining genes
   │  → Pick best accuracy with LogisticRegression
   ▼
Top 10 genes identified
   │
   ▼
Keep Top 6 genes only
   │
   ▼
train_test_split (80/20, stratified)
   │
   ▼
StandardScaler (fit on train only)
   │
   ▼
LogisticRegression (final model)
   │
   ▼
Evaluate + Save artefacts
   │
   ▼
FastAPI  →  Frontend  →  Prediction: Normal / Abnormal
```

---

## 🌐 API Endpoints

| Method | Endpoint    | Description                        |
|--------|-------------|------------------------------------|
| GET    | `/`         | API welcome message                |
| GET    | `/health`   | Liveness probe                     |
| GET    | `/genes`    | List of 6 selected genes           |
| POST   | `/predict`  | Predict Normal/Abnormal            |
| GET    | `/docs`     | Interactive Swagger UI             |


## Selected genes
{
  "selected_genes": [
    "M63391",
    "T62947",
    "D14812",
    "T51250",
    "H66976",
    "X55362"
  ]
}

## ⚕️ Disclaimer

> This project is for **research and portfolio purposes only**.  
> It is **not** a clinical decision support tool.  
> Always consult a qualified medical professional for health-related decisions.
