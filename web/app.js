/**
 * ScamGuard PRO — Production Web Application Frontend Logic
 * Version 2.0 (Ensemble Architecture & Forensic Intelligence)
 */

// Application State
const state = {
  apiBase: window.location.origin ? `${window.location.origin}/api/v1` : 'http://localhost:8000/api/v1',
  sessionId: getOrCreateSessionId(),
  currentRequestId: null,
  currentText: null,
  currentDetectionData: null,
  sandboxTimer: null,
};

// Preset Sample Messages for Quick Testing
const SAMPLES = {
  phishing: "URGENT: Chase Bank alert! Your online access has been temporarily suspended due to 3 suspicious login attempts. Verify immediately at https://chase-security-verify.xyz/login within 24 hours to prevent permanent closure.",
  otp: "Your verification code is 482910. Do not share this OTP with anyone. A customer care executive is waiting on the line to confirm your card details and unblock your account.",
  delivery: "USPS Notice: Your package US-8921-992 cannot be delivered due to an incomplete street address. Update your delivery address within 12 hours at https://usps-redelivery-tracking.club/status to avoid return to sender.",
  crypto: "ELON MUSK GIVEAWAY: 5,000 BTC & 50,000 ETH airdrop event! Send 0.1 BTC to the official wallet and receive 0.2 BTC back instantly. Claim now at https://tesla-crypto-promo.top before time runs out!",
  safe: "Hey Sarah! Are we still meeting for lunch at the cafe around 1:00 PM today? Let me know if you want me to grab a table outside.",
  ambiguous: "Ok call me"
};

// Batch Evaluation Preset (10 Sample Messages)
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

// Threat Vector Meta Mapping
const VECTOR_META = {
  urgency_coercion: { label: "Urgency & Coercion", icon: "⏱️" },
  financial_risk: { label: "Financial / Money Risk", icon: "💳" },
  credential_harvesting: { label: "Credential Harvesting", icon: "🔑" },
  impersonation: { label: "Brand Impersonation", icon: "🎭" },
  link_domain_risk: { label: "Suspicious Link / Typosquatting", icon: "🌐" },
  social_engineering: { label: "Social Engineering / Lure", icon: "🎣" }
};

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSessionDisplay();
  checkApiHealth();
  loadBenchmarkData();
  loadAuditHistory();
  initSandbox();
});

// Theme Management (Dark Mode Default)
function initTheme() {
  const savedTheme = localStorage.getItem("scamguard_theme") || "dark";
  applyTheme(savedTheme);
}

function toggleTheme() {
  const isDark = document.documentElement.classList.contains("dark");
  const newTheme = isDark ? "light" : "dark";
  applyTheme(newTheme);
  localStorage.setItem("scamguard_theme", newTheme);
}

function applyTheme(theme) {
  const icon = document.getElementById("theme-icon");
  const text = document.getElementById("theme-text");
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
    if (icon) icon.textContent = "☀️";
    if (text) text.textContent = "Light";
  } else {
    document.documentElement.classList.remove("dark");
    if (icon) icon.textContent = "🌙";
    if (text) text.textContent = "Dark";
  }
}

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

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) targetTab.classList.add("active");

  const desktopBtn = document.getElementById(`nav-${tabId}`);
  if (desktopBtn) desktopBtn.classList.add("active");

  if (tabId === "benchmark") loadBenchmarkData();
  if (tabId === "history") loadAuditHistory();
  if (tabId === "sandbox") initSandbox();
}

// Health Check
async function checkApiHealth() {
  const badge = document.getElementById("api-status-badge");
  const text = document.getElementById("api-status-text");
  try {
    const res = await fetch(`${state.apiBase}/health`);
    if (res.ok) {
      const data = await res.json();
      badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800";
      text.textContent = data.model_loaded ? "Backend & ML Live" : "API Live (Heuristics)";
    } else {
      throw new Error("HTTP " + res.status);
    }
  } catch (err) {
    badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800";
    text.textContent = "Backend Offline";
  }
}

// Input Helpers
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
    state.currentText = text;
    state.currentDetectionData = data;

    displayResults(data);

  } catch (err) {
    alert("Analysis Failed: " + err.message);
  } finally {
    btn.disabled = false;
    btnSpinner.classList.add("hidden");
    btnText.textContent = "Run Forensic Threat Analysis";
  }
}

// Render Results Dashboard
function displayResults(data) {
  document.getElementById("results-empty").classList.add("hidden");
  const card = document.getElementById("results-card");
  card.classList.remove("hidden");

  const banner = document.getElementById("result-tier-banner");
  const icon = document.getElementById("result-tier-icon");
  const title = document.getElementById("result-tier-title");
  const subtitle = document.getElementById("result-tier-subtitle");
  const scoreEl = document.getElementById("result-score");
  const conf = document.getElementById("result-confidence");
  const stageBadge = document.getElementById("result-stage-badge");
  const latency = document.getElementById("result-latency");

  const score = Math.round(data.risk_score);
  title.textContent = data.classification;
  scoreEl.innerHTML = `${score}<span class="text-xs font-normal opacity-70">/100</span>`;
  conf.textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
  stageBadge.textContent = data.stage_applied;
  latency.textContent = `${data.processing_time_ms.toFixed(1)} ms`;

  // Circular SVG Gauge Animation
  const gaugeBar = document.getElementById("gauge-circle-bar");
  if (gaugeBar) {
    const circumference = 2 * Math.PI * 45; // ~282.74
    gaugeBar.style.strokeDasharray = `${circumference} ${circumference}`;
    const offset = circumference - (score / 100) * circumference;
    gaugeBar.style.strokeDashoffset = offset;
  }

  // Tier Colors & Banner Styling
  banner.className = "p-5 rounded-2xl border flex flex-col sm:flex-row items-center justify-between gap-4 ";
  if (data.classification === "Likely Scam") {
    banner.classList.add("tier-scam");
    icon.textContent = "🚨";
    subtitle.textContent = "High Scam Risk: Financial or Identity Compromise Likely";
    if (gaugeBar) gaugeBar.style.stroke = "#ef4444";
  } else if (data.classification === "Suspicious") {
    banner.classList.add("tier-suspicious");
    icon.textContent = "⚠️";
    subtitle.textContent = "Caution: Contains Anomalous Urgency or Unknown Links";
    if (gaugeBar) gaugeBar.style.stroke = "#f59e0b";
  } else if (data.classification === "Unable to Determine") {
    banner.classList.add("tier-undetermined");
    icon.textContent = "❓";
    subtitle.textContent = "Ambiguous Input: Insufficient Evidence for High-Confidence Label";
    if (gaugeBar) gaugeBar.style.stroke = "#8b5cf6";
  } else {
    banner.classList.add("tier-safe");
    icon.textContent = "🛡️";
    subtitle.textContent = "Benign Content: No High-Risk Vectors Detected";
    if (gaugeBar) gaugeBar.style.stroke = "#10b981";
  }

  // Redacted Text Preview (if applicable)
  const redBox = document.getElementById("redacted-preview-box");
  const redText = document.getElementById("redacted-preview-text");
  if (data.pii_redacted && data.redacted_preview) {
    redBox.classList.remove("hidden");
    redText.textContent = data.redacted_preview;
  } else {
    redBox.classList.add("hidden");
  }

  // 1. Visual Threat Inspector (Annotated Tokens)
  const annotatedBox = document.getElementById("annotated-message-box");
  if (annotatedBox) {
    if (data.annotated_message && data.annotated_message.html) {
      annotatedBox.innerHTML = data.annotated_message.html;
    } else if (data.redacted_preview) {
      annotatedBox.textContent = data.redacted_preview;
    } else {
      annotatedBox.textContent = state.currentText || "";
    }
  }

  // 2. Multidimensional Threat Vectors (6 Vectors)
  const vectorsGrid = document.getElementById("threat-vectors-grid");
  const primBadge = document.getElementById("primary-vector-badge");
  if (vectorsGrid) {
    vectorsGrid.innerHTML = "";
    const vectors = data.threat_vectors ? data.threat_vectors.scores : null;
    const ratings = data.threat_vectors ? data.threat_vectors.ratings : null;
    const prim = data.threat_vectors ? (data.threat_vectors.primary_vector || "None") : "None";

    if (primBadge) {
      primBadge.textContent = `Primary: ${prim.replace(/_/g, " ").toUpperCase()}`;
      primBadge.className = prim === "none" ? "badge-neutral text-[10px]" : "badge-threat text-[10px]";
    }

    if (vectors) {
      Object.entries(vectors).forEach(([key, vScore]) => {
        const meta = VECTOR_META[key] || { label: key, icon: "🔍" };
        const rating = ratings ? (ratings[key] || "LOW") : "LOW";

        let barColor = "bg-emerald-500";
        let ratingBadgeClass = "text-emerald-700 bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800";
        if (rating === "CRITICAL") {
          barColor = "bg-rose-500";
          ratingBadgeClass = "text-rose-700 bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-800";
        } else if (rating === "HIGH") {
          barColor = "bg-amber-500";
          ratingBadgeClass = "text-amber-700 bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800";
        } else if (rating === "MEDIUM") {
          barColor = "bg-yellow-500";
          ratingBadgeClass = "text-yellow-700 bg-yellow-50 dark:bg-yellow-950/60 border-yellow-200 dark:border-yellow-800";
        }

        const div = document.createElement("div");
        div.className = "p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1.5";
        div.innerHTML = `
          <div class="flex items-center justify-between font-semibold">
            <span class="flex items-center gap-1.5 text-slate-800 dark:text-slate-200">
              <span>${meta.icon}</span> <span>${meta.label}</span>
            </span>
            <div class="flex items-center gap-1.5">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold border ${ratingBadgeClass}">${rating}</span>
              <span class="font-mono text-[11px] text-slate-500">${vScore.toFixed(0)}%</span>
            </div>
          </div>
          <div class="vector-bar-bg">
            <div class="vector-bar-fill ${barColor}" style="width: ${vScore}%"></div>
          </div>
        `;
        vectorsGrid.appendChild(div);
      });
    }
  }

  // 3. URL & Domain Forensic Intelligence
  const urlCard = document.getElementById("url-intel-card");
  const urlDetails = document.getElementById("url-intel-details");
  if (urlCard && urlDetails) {
    const urls = (data.url_intelligence && data.url_intelligence.details) || [];
    if (urls.length > 0) {
      urlCard.classList.remove("hidden");
      urlDetails.innerHTML = urls.map(u => {
        const typosquatWarning = u.is_typosquat ? 
          `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-700 dark:bg-rose-950/80 dark:text-rose-300 border border-rose-300 dark:border-rose-800">⚠️ Typosquatting: Target Brand <strong>${u.typosquat_target}</strong> (Levenshtein Dist: ${u.typosquat_distance})</span>` : "";
        const riskyTldWarning = u.risky_tld ? 
          `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 dark:bg-amber-950/80 dark:text-amber-300 border border-amber-300 dark:border-amber-800">Suspicious TLD: .${u.tld}</span>` : "";
        const entropyBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">Entropy: ${u.entropy.toFixed(2)}</span>`;
        const shortenerBadge = u.is_shortener ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700 dark:bg-purple-950/80 dark:text-purple-300">URL Shortener</span>` : "";

        return `
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1.5 font-mono text-[11px]">
            <div class="flex items-center justify-between flex-wrap gap-1 font-bold text-slate-800 dark:text-slate-200">
              <span class="break-all text-indigo-600 dark:text-indigo-400">${u.raw_url}</span>
              <span class="px-2 py-0.5 rounded text-[10px] ${u.risk_score >= 50 ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'}">Domain Threat: ${u.risk_score.toFixed(0)}/100</span>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-slate-500 dark:text-slate-400 font-sans">Hostname: <strong>${u.domain}</strong></span>
              ${typosquatWarning}
              ${riskyTldWarning}
              ${entropyBadge}
              ${shortenerBadge}
            </div>
            ${u.risk_factors && u.risk_factors.length > 0 ? `<div class="text-[10px] text-rose-600 dark:text-rose-400 font-sans">Flags: ${u.risk_factors.join(" • ")}</div>` : ''}
          </div>
        `;
      }).join("");
    } else {
      urlCard.classList.add("hidden");
    }
  }

  // 4. ML Ensemble Token Attributions
  const attrList = document.getElementById("ml-attributions-list");
  if (attrList) {
    const tokens = data.token_attributions || [];
    if (tokens.length > 0) {
      attrList.innerHTML = tokens.map(t => {
        const isScam = t.weight > 0;
        const badgeColor = isScam 
          ? "bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-900"
          : "bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900";
        const sign = isScam ? "+" : "";
        return `<span class="px-2 py-0.5 rounded-full font-mono border ${badgeColor}" title="Weight: ${t.weight.toFixed(2)}">${t.token} <strong class="opacity-80">${sign}${t.weight.toFixed(1)}</strong></span>`;
      }).join("");
    } else {
      attrList.innerHTML = `<span class="text-xs text-slate-400 italic">No dominant token-level weight signals identified.</span>`;
    }
  }

  // 5. Actionable Forensic Recommendations
  const recList = document.getElementById("recommendations-list");
  if (recList) {
    recList.innerHTML = "";
    (data.suggested_actions || data.reasons || []).forEach(act => {
      const li = document.createElement("li");
      li.className = "flex items-start gap-1.5";
      li.innerHTML = `<span class="text-indigo-600 dark:text-indigo-400 mt-0.5">•</span><span>${act}</span>`;
      recList.appendChild(li);
    });
  }
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
      alert("Feedback recorded. Thank you for contributing to model evaluation!");
    }
  } catch (err) {
    console.error("Feedback error", err);
  }
}

// ==========================================
// TAB 2: LIVE "WHAT-IF" SIMULATION SANDBOX
// ==========================================

function initSandbox() {
  const input = document.getElementById("sandbox-input");
  if (input && !input.value.trim()) {
    loadSandboxSample('bank');
  }
}

function loadSandboxSample(type) {
  const input = document.getElementById("sandbox-input");
  if (!input) return;
  if (type === "bank") {
    input.value = "URGENT: Chase Bank alert! Your online access has been temporarily suspended due to 3 suspicious login attempts. Verify immediately at https://chase-security-verify.xyz/login within 24 hours to prevent permanent closure.";
  } else if (type === "delivery") {
    input.value = "USPS Notice: Your package US-8921-992 cannot be delivered due to an incomplete street address. Update your delivery address within 12 hours at https://usps-redelivery-tracking.club/status to avoid return to sender.";
  }
  runSandboxAnalysis();
}

function sandboxTransform(action) {
  const input = document.getElementById("sandbox-input");
  if (!input) return;
  let text = input.value;

  if (action === "remove_urls") {
    text = text.replace(/https?:\/\/[^\s]+/gi, "[LINK REMOVED]");
  } else if (action === "remove_urgency") {
    text = text.replace(/\b(urgent|immediately|within 24 hours|within 12 hours|suspended|temporarily suspended|final notice|expires|deadline|act now|alert)\b/gi, "[NEUTRALIZED]");
  } else if (action === "mask_pii") {
    text = text.replace(/\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|\b\d{10,12}\b|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/gi, "[REDACTED]");
  }

  input.value = text;
  runSandboxAnalysis();
}

function runSandboxAnalysis() {
  clearTimeout(state.sandboxTimer);
  state.sandboxTimer = setTimeout(async () => {
    const input = document.getElementById("sandbox-input");
    const text = input ? input.value.trim() : "";
    if (!text) {
      document.getElementById("sandbox-score").textContent = "0";
      document.getElementById("sandbox-classification").textContent = "Awaiting Input";
      return;
    }

    const t0 = performance.now();
    try {
      const res = await fetch(`${state.apiBase}/detect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          source: "MANUAL",
          bypass_prefilter: true,
          redact_pii_before_analysis: false
        })
      });

      if (!res.ok) return;
      const data = await res.json();
      const latency = (performance.now() - t0).toFixed(1);

      document.getElementById("sandbox-latency").textContent = `${latency} ms`;
      document.getElementById("sandbox-score").innerHTML = `${Math.round(data.risk_score)}<span class="text-xs font-normal opacity-70">/100</span>`;
      document.getElementById("sandbox-classification").textContent = data.classification;
      document.getElementById("sandbox-summary").textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}% • Stage: ${data.stage_applied}`;

      // Banner style
      const banner = document.getElementById("sandbox-result-banner");
      banner.className = "p-4 rounded-xl border flex items-center justify-between ";
      if (data.classification === "Likely Scam") {
        banner.classList.add("tier-scam");
      } else if (data.classification === "Suspicious") {
        banner.classList.add("tier-suspicious");
      } else {
        banner.classList.add("tier-safe");
      }

      // Render miniature threat vectors
      const vecContainer = document.getElementById("sandbox-vectors-list");
      if (vecContainer && data.threat_vectors && data.threat_vectors.scores) {
        vecContainer.innerHTML = "";
        Object.entries(data.threat_vectors.scores).forEach(([k, score]) => {
          const meta = VECTOR_META[k] || { label: k, icon: "•" };
          let color = "bg-emerald-500";
          if (score >= 65) color = "bg-rose-500";
          else if (score >= 35) color = "bg-amber-500";

          const row = document.createElement("div");
          row.className = "space-y-1";
          row.innerHTML = `
            <div class="flex items-center justify-between text-[11px] font-medium text-slate-700 dark:text-slate-300">
              <span>${meta.icon} ${meta.label}</span>
              <span class="font-mono">${score.toFixed(0)}%</span>
            </div>
            <div class="vector-bar-bg">
              <div class="vector-bar-fill ${color}" style="width: ${score}%"></div>
            </div>
          `;
          vecContainer.appendChild(row);
        });
      }

    } catch (e) {
      console.error("Sandbox error", e);
    }
  }, 200);
}

// ==========================================
// FORENSIC INCIDENT REPORT & EXPORT
// ==========================================

async function openForensicReportModal() {
  if (!state.currentText) {
    alert("Please inspect a message first to generate a forensic report.");
    return;
  }

  const modal = document.getElementById("forensic-report-modal");
  const modalContent = document.getElementById("modal-report-content");
  modalContent.innerHTML = `<div class="p-6 text-center text-slate-500"><span class="spinner"></span> Compiling Forensic Artifacts & IOCs...</div>`;
  modal.classList.remove("hidden");

  try {
    const res = await fetch(`${state.apiBase}/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: state.currentText,
        source: "MANUAL",
        bypass_prefilter: true
      })
    });

    if (!res.ok) throw new Error("Failed to compile forensic report");
    const rep = await res.json();

    document.getElementById("modal-report-id").textContent = rep.report_id;

    modalContent.innerHTML = `
      <div class="space-y-4 font-sans">
        <div class="bg-slate-50 dark:bg-slate-950 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Investigation Time</span>
            <span class="font-mono text-slate-800 dark:text-slate-200">${rep.timestamp_utc}</span>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Verdict</span>
            <span class="font-bold ${rep.classification === 'Likely Scam' ? 'text-rose-600' : 'text-emerald-600'}">${rep.classification} (${rep.risk_score.toFixed(0)}/100)</span>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Primary Threat Vector</span>
            <span class="font-semibold text-slate-800 dark:text-slate-200">${(rep.primary_threat_vector || "None").replace(/_/g, " ").toUpperCase()}</span>
          </div>
        </div>

        <div>
          <span class="text-slate-400 block text-[10px] uppercase font-bold mb-1">SHA-256 Message Cryptographic Hash</span>
          <div class="p-2 bg-slate-100 dark:bg-slate-800 rounded font-mono text-[11px] break-all select-all text-slate-700 dark:text-slate-300">
            ${rep.message_hash_sha256}
          </div>
        </div>

        <div>
          <span class="text-slate-400 block text-[10px] uppercase font-bold mb-1">Indicators of Compromise (IOCs)</span>
          ${rep.indicators_of_compromise && rep.indicators_of_compromise.length > 0 ? `
            <div class="border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 dark:bg-slate-800 text-slate-500 text-[10px] uppercase font-semibold">
                  <tr>
                    <th class="px-3 py-1.5">Type</th>
                    <th class="px-3 py-1.5">Artifact / Value</th>
                    <th class="px-3 py-1.5">Risk</th>
                    <th class="px-3 py-1.5">Notes</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
                  ${rep.indicators_of_compromise.map(ioc => `
                    <tr>
                      <td class="px-3 py-1.5 text-indigo-500 font-sans text-[10px]">${ioc.type}</td>
                      <td class="px-3 py-1.5 text-slate-800 dark:text-slate-200 break-all">${ioc.value}</td>
                      <td class="px-3 py-1.5 font-bold ${ioc.risk_score >= 50 ? 'text-rose-500' : 'text-slate-500'}">${ioc.risk_score.toFixed(0)}</td>
                      <td class="px-3 py-1.5 text-slate-400 font-sans text-[10px]">${ioc.notes}</td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          ` : `<div class="text-xs text-slate-400 italic p-2 bg-slate-50 dark:bg-slate-950 rounded">No specific indicators or malicious domains extracted.</div>`}
        </div>

        <div>
          <span class="text-slate-400 block text-[10px] uppercase font-bold mb-1">Incident Playbook Response Actions</span>
          <ul class="space-y-1 text-xs text-slate-700 dark:text-slate-300">
            ${rep.incident_playbook_actions.map(act => `<li class="flex items-start gap-1.5"><span class="text-indigo-500">•</span><span>${act}</span></li>`).join("")}
          </ul>
        </div>
      </div>
    `;

  } catch (err) {
    modalContent.innerHTML = `<div class="p-4 bg-rose-50 text-rose-700 rounded-xl">Error: ${err.message}</div>`;
  }
}

function closeForensicReportModal() {
  document.getElementById("forensic-report-modal").classList.add("hidden");
}

function exportReportJSON() {
  if (!state.currentDetectionData) {
    alert("Please inspect a message first before exporting JSON.");
    return;
  }
  const blob = new Blob([JSON.stringify(state.currentDetectionData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `scamguard-forensic-report-${Date.now()}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ==========================================
// RESEARCH BENCHMARK & AUDIT HISTORY
// ==========================================

async function loadBenchmarkData() {
  try {
    const res = await fetch(`${state.apiBase}/benchmark`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data.models) return;

    // Update KPI Cards
    const twoStage = data.models["two_stage_selective_architecture"];
    const mlModel = data.models["machine_learning_classifier"];

    if (twoStage) {
      const redEl = document.getElementById("kpi-traffic-reduction");
      if (redEl) redEl.textContent = `${twoStage.request_reduction_pct.toFixed(2)}%`;
      const latEl = document.getElementById("kpi-latency");
      if (latEl && twoStage.latency_ms) latEl.textContent = `${twoStage.latency_ms.toFixed(2)} ms`;
    }

    if (mlModel) {
      const accEl = document.getElementById("kpi-accuracy");
      if (accEl) accEl.textContent = `${(mlModel.accuracy * 100).toFixed(2)}%`;
      const fprEl = document.getElementById("kpi-fpr");
      if (fprEl) fprEl.textContent = `${(mlModel.false_positive_rate * 100).toFixed(2)}%`;
    }

    const tbody = document.getElementById("benchmark-table-body");
    if (!tbody) return;
    tbody.innerHTML = "";

    const modelNames = {
      "rule_based_baseline": "Model 1: Heuristic Rule Baseline",
      "machine_learning_classifier": "Model 2: ML Soft-Voting Ensemble (Word+Char TF-IDF)",
      "hybrid_rule_ml": "Model 3: Hybrid Detection Engine (Rules + ML)",
      "two_stage_selective_architecture": "Model 4: Two-Stage Architecture (Edge Prefilter + Remote)"
    };

    for (const [key, m] of Object.entries(data.models)) {
      const isSelected = key === "two_stage_selective_architecture";
      const tr = document.createElement("tr");
      if (isSelected) tr.className = "bg-indigo-50/50 dark:bg-indigo-950/40 font-semibold";

      tr.innerHTML = `
        <td class="px-5 py-3 font-medium text-slate-900 dark:text-slate-100">${modelNames[key] || key}</td>
        <td class="px-4 py-3 text-center font-mono">${(m.accuracy * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.precision * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.recall * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.f1_score * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-rose-600 dark:text-rose-400">${(m.false_positive_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-amber-600 dark:text-amber-400">${(m.false_negative_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${m.backend_requests} / ${data.test_samples}</td>
        <td class="px-4 py-3 text-center font-mono text-indigo-700 dark:text-indigo-400 font-bold">${m.request_reduction_pct.toFixed(1)}%</td>
      `;
      tbody.appendChild(tr);
    }

  } catch (err) {
    console.error("Benchmark load error", err);
  }
}

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

    if (!data.items || data.items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-8 text-center text-slate-400">No detection audits recorded yet for this session.</td></tr>`;
      return;
    }

    data.items.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="px-5 py-3 text-slate-600 dark:text-slate-400 font-mono text-[11px]">${item.timestamp.replace("T", " ").substring(0, 19)}</td>
        <td class="px-4 py-3 font-medium text-slate-700 dark:text-slate-300">${item.source}</td>
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

// ==========================================
// TAB 4: BATCH EVALUATOR
// ==========================================

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
  container.innerHTML = `<div class="p-6 bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 text-center"><span class="spinner"></span> Running Stage 1 vs Stage 2 batch benchmark...</div>`;

  try {
    const res = await fetch(`${state.apiBase}/evaluate-batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages, use_prefilter: true })
    });
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    container.innerHTML = `
      <div class="bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/60 rounded-2xl p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
        <div>
          <span class="text-xs text-indigo-900 dark:text-indigo-300 block font-medium">Total Messages</span>
          <span class="text-2xl font-black text-indigo-950 dark:text-indigo-100 font-mono">${data.total_messages}</span>
        </div>
        <div>
          <span class="text-xs text-emerald-900 dark:text-emerald-300 block font-medium">Filtered Locally (Edge)</span>
          <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400 font-mono">${data.filtered_locally}</span>
        </div>
        <div>
          <span class="text-xs text-amber-900 dark:text-amber-300 block font-medium">Routed to Backend</span>
          <span class="text-2xl font-black text-amber-600 dark:text-amber-400 font-mono">${data.routed_to_backend}</span>
        </div>
        <div>
          <span class="text-xs text-indigo-900 dark:text-indigo-300 block font-medium">Server Traffic Saved</span>
          <span class="text-2xl font-black text-indigo-600 dark:text-indigo-400 font-mono">${data.request_reduction_pct}%</span>
        </div>
      </div>
      <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-4 overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 dark:bg-slate-800/60 text-slate-500 dark:text-slate-400 uppercase font-semibold">
            <tr>
              <th class="px-4 py-2">Message Snippet</th>
              <th class="px-4 py-2">Routing</th>
              <th class="px-4 py-2">Classification</th>
              <th class="px-4 py-2">Risk Score</th>
              <th class="px-4 py-2">Latency</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
            ${data.results.map(r => `
              <tr>
                <td class="px-4 py-2 text-slate-700 dark:text-slate-200 font-sans text-xs">${r.text_snippet}</td>
                <td class="px-4 py-2 font-semibold ${r.prefilter_routed ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'}">${r.prefilter_routed ? 'Routed to Cloud' : 'Filtered on Device'}</td>
                <td class="px-4 py-2 text-slate-800 dark:text-slate-200">${r.classification}</td>
                <td class="px-4 py-2 text-slate-800 dark:text-slate-200">${r.risk_score.toFixed(0)}</td>
                <td class="px-4 py-2 text-slate-400 dark:text-slate-500">${r.processing_time_ms.toFixed(1)} ms</td>
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
