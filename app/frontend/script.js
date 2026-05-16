/**
 * script.js — ColonAI Frontend Logic
 *
 * Workflow:
 *  1. On load  → GET /genes  → build input fields dynamically
 *  2. On submit → POST /predict → display result + confidence bar
 *  3. Demo button → fills fields with realistic gene expression values
 */

"use strict";

// ── Config ────────────────────────────────────────────────────────────────────
const API_BASE = window.location.origin;   // same host as FastAPI

// ── State ─────────────────────────────────────────────────────────────────────
let selectedGenes = [];
// Demo values mapping (can be updated to match backend or user input)
// Demo presets mapping (two examples: abnormal and normal)
const DEMO_PRESETS = {
  abnormal: {
    M63391: 15,
    T62947: -20,
    D14812: 18,
    T51250: -17,
    H66976: 22,
    X55362: -19,
  },
  normal: {
    M63391: 3.25,
    T62947: -4.10,
    D14812: 5.42,
    T51250: -3.88,
    H66976: 4.67,
    X55362: -5.21,
  },
};

// Toggle state: false -> next click uses 'abnormal', true -> 'normal'
let demoToggle = false;

// ── DOM references ────────────────────────────────────────────────────────────
const loadingState   = document.getElementById("loading-state");
const errorState     = document.getElementById("error-state");
const predictorPanel = document.getElementById("predictor-panel");
const errorMessage   = document.getElementById("error-message");
const geneInputsDiv  = document.getElementById("gene-inputs");
const predictForm    = document.getElementById("predict-form");
const predictBtn     = document.getElementById("predict-btn");
const resetBtn       = document.getElementById("reset-btn");
const fillDemoBtn    = document.getElementById("fill-demo-btn");
const resultCard     = document.getElementById("result-card");
const resultBadge    = document.getElementById("result-badge");
const confidenceBar  = document.getElementById("confidence-bar");
const confidenceVal  = document.getElementById("confidence-value");
const closeResult    = document.getElementById("close-result");
const statusDot      = document.getElementById("status-indicator");
const heroGeneCount  = document.getElementById("hero-gene-count");

// ════════════════════════════════════════════════════════════════════════════
//  1. LOAD GENES
// ════════════════════════════════════════════════════════════════════════════
async function loadGenes() {
  // Reset UI
  loadingState.classList.remove("hidden");
  errorState.classList.add("hidden");
  predictorPanel.classList.add("hidden");
  statusDot.className = "status-dot loading";

  try {
    const res  = await fetch(`${API_BASE}/genes`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    selectedGenes = data.selected_genes;
    if (!Array.isArray(selectedGenes) || selectedGenes.length === 0) {
      throw new Error("Empty gene list returned from API.");
    }

    // Update hero stat
    if (heroGeneCount) heroGeneCount.textContent = selectedGenes.length;

    buildForm(selectedGenes);

    loadingState.classList.add("hidden");
    predictorPanel.classList.remove("hidden");
    statusDot.className = "status-dot online";

  } catch (err) {
    loadingState.classList.add("hidden");
    errorState.classList.remove("hidden");
    errorMessage.textContent = err.message || "Connection refused.";
    statusDot.className = "status-dot offline";
    console.error("[ColonAI] Failed to load genes:", err);
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  2. BUILD DYNAMIC FORM
// ════════════════════════════════════════════════════════════════════════════
function buildForm(genes) {
  geneInputsDiv.innerHTML = "";

  genes.forEach((gene, idx) => {
    const field = document.createElement("div");
    field.className = "gene-field";

    field.innerHTML = `
      <label class="gene-label" for="gene-input-${idx}">
        <span class="gene-label-dot"></span>
        <span class="gene-label-name">${escapeHtml(gene)}</span>
        <span class="gene-label-index">Gene ${idx + 1} of ${genes.length}</span>
      </label>
      <div class="gene-input-wrap">
        <input
          type="number"
          id="gene-input-${idx}"
          class="gene-input"
          data-gene="${escapeHtml(gene)}"
          placeholder="e.g. 0.45"
          step="0.0001"
          autocomplete="off"
        />
      </div>
    `;

    geneInputsDiv.appendChild(field);
  });
}

// ════════════════════════════════════════════════════════════════════════════
//  3. PREDICT
// ════════════════════════════════════════════════════════════════════════════
predictForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();
  resultCard.classList.add("hidden");

  // Collect + validate inputs
  const inputs = geneInputsDiv.querySelectorAll(".gene-input");
  const geneValues = {};
  let hasError = false;

  inputs.forEach((input) => {
    const val = input.value.trim();
    if (val === "" || isNaN(Number(val))) {
      input.classList.add("error");
      hasError = true;
    } else {
      input.classList.remove("error");
      geneValues[input.dataset.gene] = parseFloat(val);
    }
  });

  if (hasError) {
    shakeForm();
    return;
  }

  // Send request
  setLoadingState(true);

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ genes: geneValues }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || `HTTP ${res.status}`);
    }

    showResult(data.prediction, data.confidence);

  } catch (err) {
    alert(`Prediction error: ${err.message}`);
    console.error("[ColonAI] Predict error:", err);
  } finally {
    setLoadingState(false);
  }
});

// ════════════════════════════════════════════════════════════════════════════
//  4. SHOW RESULT
// ════════════════════════════════════════════════════════════════════════════
function showResult(prediction, confidence) {
  const isAbnormal = prediction.toLowerCase() === "abnormal";

  // Badge
  resultBadge.textContent = isAbnormal ? "⚠️ Abnormal" : "✅ Normal";
  resultBadge.className   = `result-badge ${isAbnormal ? "abnormal" : "normal"}`;

  // Confidence bar (animate after brief delay)
  const pct = Math.round(confidence * 100);
  confidenceBar.style.width = "0%";
  confidenceVal.textContent = `${pct}%`;

  if (isAbnormal) {
    confidenceBar.style.background = "linear-gradient(90deg, #ef4444, #f87171)";
  } else {
    confidenceBar.style.background = "linear-gradient(90deg, #10b981, #34d399)";
  }

  resultCard.classList.remove("hidden");

  // Animate bar
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      confidenceBar.style.width = `${pct}%`;
    });
  });

  // Scroll to result
  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ════════════════════════════════════════════════════════════════════════════
//  5. DEMO VALUES
// ════════════════════════════════════════════════════════════════════════════
fillDemoBtn.addEventListener("click", () => {
  const inputs = geneInputsDiv.querySelectorAll(".gene-input");
  if (!inputs || inputs.length === 0) {
    alert("Aucun champ de gène chargé — rechargez la page ou démarrez l'API backend.");
    return;
  }

  // Determine which preset to use based on toggle (first click -> abnormal)
  const presetKey = demoToggle ? "normal" : "abnormal";
  const preset = DEMO_PRESETS[presetKey] || {};
  demoToggle = !demoToggle;

  // Fallback seeds for any genes not in the preset
  const seeds = [0.83, -1.42, 0.27, 1.15, -0.63, 0.44, -1.08, 0.92, -0.31, 1.67];

  inputs.forEach((input, idx) => {
    const gene = input.dataset.gene;
    let value;

    if (gene && Object.prototype.hasOwnProperty.call(preset, gene)) {
      value = preset[gene];
    } else {
      const val = seeds[idx % seeds.length] + (Math.random() * 0.2 - 0.1);
      value = Number(val.toFixed(4));
    }

    // Format value: keep integers as-is, decimals to 4 places
    input.value = Number.isInteger(value) ? String(value) : Number(value).toFixed(4);

    input.classList.remove("error");
    input.classList.add("filled");
    setTimeout(() => input.classList.remove("filled"), 600);
  });

  clearErrors();
  resultCard.classList.add("hidden");
});

// ════════════════════════════════════════════════════════════════════════════
//  6. RESET
// ════════════════════════════════════════════════════════════════════════════
resetBtn.addEventListener("click", () => {
  const inputs = geneInputsDiv.querySelectorAll(".gene-input");
  inputs.forEach((input) => {
    input.value = "";
    input.classList.remove("error");
  });
  resultCard.classList.add("hidden");
});

closeResult.addEventListener("click", () => {
  resultCard.classList.add("hidden");
});

// ════════════════════════════════════════════════════════════════════════════
//  HELPERS
// ════════════════════════════════════════════════════════════════════════════
function setLoadingState(loading) {
  predictBtn.disabled = loading;
  predictBtn.innerHTML = loading
    ? '<span class="btn-spinner"></span> Predicting…'
    : '<span class="btn-icon">🔬</span> Run Prediction';
}

function clearErrors() {
  geneInputsDiv.querySelectorAll(".gene-input.error").forEach((el) =>
    el.classList.remove("error")
  );
}

function shakeForm() {
  predictForm.classList.add("shake");
  setTimeout(() => predictForm.classList.remove("shake"), 400);
}

function escapeHtml(str) {
  const d = document.createElement("div");
  d.textContent = str;
  return d.innerHTML;
}

// ── Shake animation (injected) ────────────────────────────────────────────────
const shakeStyle = document.createElement("style");
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%       { transform: translateX(-8px); }
    40%       { transform: translateX(8px); }
    60%       { transform: translateX(-5px); }
    80%       { transform: translateX(5px); }
  }
  .shake { animation: shake 0.4s ease; }
  .gene-input.filled { border-color: var(--accent-cyan) !important; transition: border-color 0.3s; }
`;
document.head.appendChild(shakeStyle);

// ── Boot ──────────────────────────────────────────────────────────────────────
loadGenes();
