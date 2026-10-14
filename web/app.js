/**
 * ScamGuard AI — Client Web Application Logic
 */

// Configuration & State
const state = {
  apiBase: window.location.origin ? `${window.location.origin}/api/v1` : 'http://localhost:8000/api/v1',
  sessionId: getOrCreateSessionId(),
  currentRequestId: null,
};

// Preset sample messages
const SAMPLES = {
  phishing: "URGENT: Chase Bank alert! Your online access has been temporarily suspended due to 3 suspicious login attempts. Verify immediately at https://chase-security-verify.xyz/login within 24 hours to prevent permanent closure.",
  otp: "Your verification code is 482910. Do not share this OTP with anyone. A customer care executive is waiting on the line to confirm your card details and unblock your account.",
  lottery: "CONGRATULATIONS! You have been selected as the winner of the 2026 International Mobile Draw! You won $2,500,000 cash. Claim your prize now by sending your name to claim@global-lottery.net or call +447812938102 immediately.",
  safe: "Hey Sarah! Are we still meeting for lunch at the cafe around 1:00 PM today? Let me know if you want me to grab a table outside.",
  ambiguous: "Ok call me"
};

// Batch Evaluation Preset
const BATCH_PRESET = [
  "URGENT: Your Wells Fargo account has been blocked. Confirm your PIN at http://192.168.1.10/verify to restore access immediately.",
  "Hey mom, I will be home by 6pm for dinner. Love you!",
  "Claim your free $500 Amazon gift card now! Click bit.ly/amz-free-gift before deadline expires.",
  "Are you coming to the group study session tomorrow afternoon?",
  "FINAL NOTICE: IRS tax refund pending. Click http://irs-tax-refund.top to claim your $1,420 refund before midnight.",
  "Thanks for sending over the project notes, looks good.",
  "SECURITY ALERT: Unauthorized access detected from Moscow. Verify identity at https://secure-login.club or your email will be deleted in 12 hours.",
  "Can you pick up some milk on your way back?",
  "Congratulations! You won the UK National Lottery! Ring 09061743810 to collect your £500,000 jackpot award.",
  "Sounds good, see you soon!"
];

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initSessionDisplay();
  checkApiHealth();
  loadBenchmarkData();
  loadAuditHistory();
});

function getOrCreateSessionId() {
  let sid = localStorage.getItem("scamguard_session_id");
  if (!sid) {
    sid = "sess_" + Math.random().toString(36).substring(2, 12);
    localStorage.setItem("scamguard_session_id", sid);
  }
  return sid;
}

function initSessionDisplay() {
  const el = document.getElementById("session-id-display");
  if (el) el.value = state.sessionId;
  const urlEl = document.getElementById("api-base-url-input");
  if (urlEl) urlEl.value = state.apiBase;
}

function saveSettings() {
  const urlEl = document.getElementById("api-base-url-input");
  if (urlEl && urlEl.value.trim()) {
    state.apiBase = urlEl.value.trim();
  }
  checkApiHealth();
  alert("Settings saved successfully.");
}

// Navigation Tabs
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) targetTab.classList.add("active");

  const btn = document.getElementById(`nav-${tabId}`);
  if (btn) btn.classList.add("active");

  if (tabId === "benchmark") loadBenchmarkData();
  if (tabId === "history") loadAuditHistory();
}

// Check Backend Health
async function checkApiHealth() {
  const badge = document.getElementById("api-status-badge");
  const text = document.getElementById("api-status-text");
  try {
    const res = await fetch(`${state.apiBase}/health`);
    if (res.ok) {
      const data = await res.json();
      badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200";
      text.textContent = data.model_loaded ? "Backend & ML Live" : "API Live (Heuristic Mode)";
    } else {
      throw new Error("HTTP " + res.status);
    }
  } catch (err) {
    badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200";
    text.textContent = "Backend Offline";
  }
}

// Sample Loader
function loadSample(key) {
  const input = document.getElementById("message-input");
  if (input && SAMPLES[key]) {
    input.value = SAMPLES[key];
    updateCharCount();
  }
}

function clearInput() {
  const input = document.getElementById("message-input");
  if (input) {
    input.value = "";
    updateCharCount();
  }
}

function updateCharCount() {
  const input = document.getElementById("message-input");
  const counter = document.getElementById("char-counter");
  if (input && counter) {
    counter.textContent = `${input.value.length} / 4000`;
  }
}

// Main Detection Analysis
async function analyzeMessage() {
  const input = document.getElementById("message-input");
  const text = input ? input.value.trim() : "";
  if (!text) {
    alert("Please enter or paste a message to inspect.");
    return;
  }

  const piiRedact = document.getElementById("toggle-pii").checked;
  const prefilterEnabled = document.getElementById("toggle-prefilter").checked;
  const source = document.getElementById("source-select").value;

  const btn = document.getElementById("analyze-btn");
  const btnSpinner = document.getElementById("btn-spinner");
  const btnText = document.getElementById("btn-text");

  btn.disabled = true;
  btnSpinner.classList.remove("hidden");
  btnText.textContent = "Analyzing Threat Vectors...";

  try {
    const payload = {
      text: text,
      source: source,
      client_session_id: state.sessionId,
      bypass_prefilter: !prefilterEnabled,
      redact_pii_before_analysis: piiRedact
    };

    const res = await fetch(`${state.apiBase}/detect`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": state.sessionId
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error: ${res.status}`);
    }

    const data = await res.json();
    state.currentRequestId = data.request_id;
    displayResults(data);

  } catch (err) {
    alert("Analysis Failed: " + err.message);
  } finally {
    btn.disabled = false;
    btnSpinner.classList.add("hidden");
    btnText.textContent = "Inspect for Scam Indicators";
  }
}

// Render Results Card
function displayResults(data) {
  document.getElementById("results-empty").classList.add("hidden");
  const card = document.getElementById("results-card");
  card.classList.remove("hidden");

  const banner = document.getElementById("result-tier-banner");
  const icon = document.getElementById("result-tier-icon");
  const title = document.getElementById("result-tier-title");
  const score = document.getElementById("result-score");
  const conf = document.getElementById("result-confidence");
  const stageBadge = document.getElementById("result-stage-badge");
  const latency = document.getElementById("result-latency");

  title.textContent = data.classification;
  score.innerHTML = `${Math.round(data.risk_score)}<span class="text-xs font-normal opacity-70">/100</span>`;
  conf.textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
  stageBadge.textContent = data.stage_applied;
  latency.textContent = `${data.processing_time_ms.toFixed(1)} ms`;

  // Apply tier styling
  banner.className = "p-4 rounded-xl border flex items-center justify-between ";
  if (data.classification === "Likely Scam") {
    banner.classList.add("tier-scam");
    icon.textContent = "🚨";
  } else if (data.classification === "Suspicious") {
    banner.classList.add("tier-suspicious");
    icon.textContent = "⚠️";
  } else if (data.classification === "Unable to Determine") {
    banner.classList.add("tier-undetermined");
    icon.textContent = "❓";
  } else {
    banner.classList.add("tier-safe");
    icon.textContent = "🛡️";
  }

  // Redacted preview
  const redBox = document.getElementById("redacted-preview-box");
  const redText = document.getElementById("redacted-preview-text");
  if (data.pii_redacted && data.redacted_preview) {
    redBox.classList.remove("hidden");
    redText.textContent = data.redacted_preview;
  } else {
    redBox.classList.add("hidden");
  }

  // Indicators
  const indList = document.getElementById("indicators-list");
  const countBadge = document.getElementById("indicator-count-badge");
  indList.innerHTML = "";
  countBadge.textContent = `${data.indicators.length} detected`;

  if (data.indicators.length === 0) {
    indList.innerHTML = `<div class="text-xs text-slate-500 italic p-2 bg-slate-50 rounded-lg">No heuristic threats or suspicious URLs matched.</div>`;
  } else {
    data.indicators.forEach(ind => {
      const div = document.createElement("div");
      div.className = `indicator-card severity-${ind.severity}`;
      const snippets = ind.matched_snippets && ind.matched_snippets.length > 0 
        ? `<div class="font-mono text-[11px] mt-1 opacity-90">Matched: ${ind.matched_snippets.map(s => `"${s}"`).join(", ")}</div>` 
        : "";
      div.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-bold">[${ind.severity}] ${ind.category}</span>
        </div>
        <div class="mt-0.5">${ind.description}</div>
        ${snippets}
      `;
      indList.appendChild(div);
    });
  }

  // Breakdown values
  const mlProb = data.breakdown ? (data.breakdown.ml_probability ? data.breakdown.ml_probability * 100 : (data.breakdown.ml_risk || 0)) : 0;
  const ruleScore = data.breakdown ? (data.breakdown.rule_risk_score !== undefined ? data.breakdown.rule_risk_score : (data.breakdown.rule_risk || 0)) : 0;
  document.getElementById("breakdown-ml-prob").textContent = `${mlProb.toFixed(1)}%`;
  document.getElementById("breakdown-rule-score").textContent = `${ruleScore.toFixed(0)} / 100`;

  // Recommendations
  const recList = document.getElementById("recommendations-list");
  recList.innerHTML = "";
  (data.suggested_actions || []).forEach(act => {
    const li = document.createElement("li");
    li.className = "flex items-start gap-1.5";
    li.innerHTML = `<span class="text-indigo-600 mt-0.5">•</span><span>${act}</span>`;
    recList.appendChild(li);
  });
}

// User Feedback
async function sendFeedback(label) {
  if (!state.currentRequestId) {
    alert("No active detection result to rate.");
    return;
  }
  try {
    const res = await fetch(`${state.apiBase}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-ID": state.sessionId
      },
      body: JSON.stringify({
        request_id: state.currentRequestId,
        actual_label: label,
        user_notes: `Marked by user as ${label}`
      })
    });
    if (res.ok) {
      alert("Feedback submitted. Thank you for contributing to model auditing!");
    }
  } catch (err) {
    console.error("Feedback error", err);
  }
}

// Load Benchmark
async function loadBenchmarkData() {
  try {
    const res = await fetch(`${state.apiBase}/benchmark`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data.models) return;

    const tbody = document.getElementById("benchmark-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    const modelNames = {
      "rule_based_baseline": "Model 1: Rule-Based Baseline",
      "machine_learning_classifier": "Model 2: Machine Learning (TF-IDF + Calibrated LogReg)",
      "hybrid_rule_ml": "Model 3: Hybrid Cloud Engine (Rules + ML)",
      "two_stage_selective_architecture": "Model 4: Two-Stage Selective Architecture (Edge + Remote)"
    };

    for (const [key, m] of Object.entries(data.models)) {
      const isSelected = key === "two_stage_selective_architecture";
      const tr = document.createElement("tr");
      if (isSelected) tr.className = "bg-indigo-50/40 font-semibold";

      tr.innerHTML = `
        <td class="px-5 py-3 font-medium text-slate-900">${modelNames[key] || key}</td>
        <td class="px-4 py-3 text-center font-mono">${(m.accuracy * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.precision * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.recall * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.f1_score * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-rose-600">${(m.false_positive_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-amber-600">${(m.false_negative_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${m.backend_requests} / ${data.test_samples}</td>
        <td class="px-4 py-3 text-center font-mono text-indigo-700 font-bold">${m.request_reduction_pct.toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    }

  } catch (err) {
    console.error("Benchmark load error", err);
  }
}

// Load Audit History
async function loadAuditHistory() {
  try {
    const res = await fetch(`${state.apiBase}/history`, {
      headers: { "X-Session-ID": state.sessionId }
    });
    if (!res.ok) return;
    const data = await res.json();
    const tbody = document.getElementById("history-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-6 text-center text-slate-400">No detection audits recorded yet for this session.</td></tr>`;
      return;
    }

    data.items.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="px-5 py-3 text-slate-600 font-mono text-[11px]">${item.timestamp.replace("T", " ").substring(0, 19)}</td>
        <td class="px-4 py-3 font-medium text-slate-700">${item.source}</td>
        <td class="px-4 py-3"><span class="badge-neutral">${item.classification}</span></td>
        <td class="px-4 py-3 font-mono font-semibold">${item.risk_score.toFixed(0)}</td>
        <td class="px-4 py-3 font-mono text-slate-500">${item.latency_ms.toFixed(1)} ms</td>
        <td class="px-4 py-3 font-mono text-[10px] text-slate-400">${item.request_id.substring(0, 8)}...</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("History load error", err);
  }
}

async function clearAuditHistory() {
  if (!confirm("Are you sure you want to delete all stored audit logs for this session?")) return;
  try {
    const res = await fetch(`${state.apiBase}/history`, {
      method: "DELETE",
      headers: { "X-Session-ID": state.sessionId }
    });
    if (res.ok) {
      alert("Session history deleted.");
      loadAuditHistory();
    }
  } catch (err) {
    alert("Failed to delete history: " + err.message);
  }
}

// Batch Evaluator logic
function loadBatchPreset() {
  const area = document.getElementById("batch-input");
  if (area) area.value = BATCH_PRESET.join("\n");
}

async function runBatchEvaluation() {
  const area = document.getElementById("batch-input");
  const raw = area ? area.value.trim() : "";
  if (!raw) {
    alert("Please enter messages to benchmark.");
    return;
  }
  const messages = raw.split("\n").map(m => m.trim()).filter(m => m.length > 0);
  if (messages.length === 0) return;

  const container = document.getElementById("batch-results-container");
  container.classList.remove("hidden");
  container.innerHTML = `<div class="p-6 bg-white rounded-2xl border border-slate-200 text-center"><span class="spinner"></span> Running Stage 1 vs Stage 2 batch benchmark...</div>`;

  try {
    const res = await fetch(`${state.apiBase}/evaluate-batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages, use_prefilter: true })
    });
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    container.innerHTML = `
      <div class="bg-indigo-50 border border-indigo-100 rounded-2xl p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
        <div>
          <span class="text-xs text-indigo-900 block font-medium">Total Messages</span>
          <span class="text-2xl font-black text-indigo-950 font-mono">${data.total_messages}</span>
        </div>
        <div>
          <span class="text-xs text-emerald-900 block font-medium">Filtered Locally (Edge)</span>
          <span class="text-2xl font-black text-emerald-600 font-mono">${data.filtered_locally}</span>
        </div>
        <div>
          <span class="text-xs text-amber-900 block font-medium">Routed to Backend</span>
          <span class="text-2xl font-black text-amber-600 font-mono">${data.routed_to_backend}</span>
        </div>
        <div>
          <span class="text-xs text-indigo-900 block font-medium">Server Traffic Saved</span>
          <span class="text-2xl font-black text-indigo-600 font-mono">${data.request_reduction_pct}%</span>
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-4 overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 text-slate-500 uppercase font-semibold">
            <tr>
              <th class="px-4 py-2">Message Snippet</th>
              <th class="px-4 py-2">Routing</th>
              <th class="px-4 py-2">Classification</th>
              <th class="px-4 py-2">Risk Score</th>
              <th class="px-4 py-2">Latency</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 font-mono text-[11px]">
            ${data.results.map(r => `
              <tr>
                <td class="px-4 py-2 text-slate-700 font-sans text-xs">${r.text_snippet}</td>
                <td class="px-4 py-2 font-semibold ${r.prefilter_routed ? 'text-amber-600' : 'text-emerald-600'}">${r.prefilter_routed ? 'Routed to Cloud' : 'Filtered on Device'}</td>
                <td class="px-4 py-2">${r.classification}</td>
                <td class="px-4 py-2">${r.risk_score.toFixed(0)}</td>
                <td class="px-4 py-2 text-slate-400">${r.processing_time_ms.toFixed(1)} ms</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="p-4 bg-rose-50 text-rose-700 rounded-xl">Error: ${err.message}</div>`;
  }
}
