/**
 * ScamGuard PRO — Production Cybersecurity Web Application Frontend
 * Version 2.0 (Ensemble Architecture, URL Intel & SOC Interface)
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

// Preset Sample Messages for Deep Inspection
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

// Vector SVG Icons & Labels
const VECTOR_META = {
  urgency_coercion: {
    label: "Urgency & Psychological Coercion",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
  },
  financial_risk: {
    label: "Financial Asset / Payment Risk",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>`
  },
  credential_harvesting: {
    label: "Credential & Account Harvesting",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" /></svg>`
  },
  impersonation: {
    label: "Brand / Authority Impersonation",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>`
  },
  link_domain_risk: {
    label: "Suspicious Domain & Typosquatting",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" /></svg>`
  },
  social_engineering: {
    label: "Social Engineering & Lure",
    icon: `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>`
  }
};

// =========================================================================
// Initialization on DOM Ready
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSessionDisplay();
  checkApiHealth();
  initKeyboardShortcuts();
});

// Toast Notification Engine
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let icon = "";
  if (type === "success") {
    icon = `<svg class="w-4 h-4 text-emerald-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>`;
  } else if (type === "error") {
    icon = `<svg class="w-4 h-4 text-rose-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>`;
  } else {
    icon = `<svg class="w-4 h-4 text-indigo-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
  }

  toast.innerHTML = `
    ${icon}
    <div class="flex-1 font-medium text-xs leading-relaxed">${message}</div>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs font-bold">&times;</button>
  `;

  container.appendChild(toast);

  // Trigger smooth enter
  requestAnimationFrame(() => {
    toast.classList.add("show");
  });

  // Auto dismiss
  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 250);
  }, 4000);
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
  document.addEventListener("keydown", (e) => {
    // Ctrl + Enter or Cmd + Enter to run detection
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      const activeTab = document.querySelector(".tab-content.active");
      if (activeTab && activeTab.id === "tab-detector") {
        e.preventDefault();
        analyzeMessage();
      }
    }
    // Escape to close modal
    if (e.key === "Escape") {
      closeForensicReportModal();
    }
  });
}

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
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
    if (icon) {
      icon.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>`;
    }
  } else {
    document.documentElement.classList.remove("dark");
    if (icon) {
      icon.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>`;
    }
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
  showToast("Endpoint settings applied successfully", "success");
}

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-tab-btn").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) targetTab.classList.add("active");

  const desktopBtn = document.getElementById(`nav-${tabId}`);
  if (desktopBtn) desktopBtn.classList.add("active");

  if (tabId === "benchmark") loadBenchmarkData();
  if (tabId === "history") loadAuditHistory();
  if (tabId === "sandbox") initSandbox();
  if (tabId === "defense") updateScalabilitySim();
}

// Health Check
async function checkApiHealth() {
  const badge = document.getElementById("api-status-badge");
  const text = document.getElementById("api-status-text");
  try {
    const res = await fetch(`${state.apiBase}/health`);
    if (res.ok) {
      const data = await res.json();
      badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20";
      text.textContent = data.model_loaded ? "Ensemble v2.0 Live" : "API Connected";
    } else {
      throw new Error("HTTP " + res.status);
    }
  } catch (err) {
    badge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20";
    text.textContent = "Engine Offline";
  }
}

// Input Helpers
function loadSample(key) {
  const input = document.getElementById("message-input");
  if (input && SAMPLES[key]) {
    input.value = SAMPLES[key];
    updateCharCount();
    // Highlight chip
    document.querySelectorAll(".scenario-chip, .preset-chip").forEach(c => c.classList.remove("active"));
    const activeChip = Array.from(document.querySelectorAll(".scenario-chip, .preset-chip")).find(c => c.textContent.toLowerCase().includes(key.substring(0, 3)));
    if (activeChip) activeChip.classList.add("active");
  }
}

function clearInput() {
  const input = document.getElementById("message-input");
  if (input) {
    input.value = "";
    updateCharCount();
  }
  document.querySelectorAll(".scenario-chip, .preset-chip").forEach(c => c.classList.remove("active"));
  document.getElementById("results-card").classList.add("hidden");
  document.getElementById("results-empty").classList.remove("hidden");
}

function updateCharCount() {
  const input = document.getElementById("message-input");
  const counter = document.getElementById("char-counter");
  if (input && counter) {
    counter.textContent = `${input.value.length} / 4000`;
  }
}

// Number Counter Animation Helper
function animateValue(el, start, end, duration) {
  const startTime = performance.now();
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    // Smooth ease-out quad
    const ease = 1 - (1 - progress) * (1 - progress);
    const current = Math.floor(start + (end - start) * ease);
    el.innerHTML = `${current}<span class="text-xs font-normal opacity-70">/100</span>`;
    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }
  requestAnimationFrame(update);
}

// =========================================================================
// Main Detection Execution
// =========================================================================
async function analyzeMessage() {
  const input = document.getElementById("message-input");
  const text = input ? input.value.trim() : "";
  if (!text) {
    showToast("Please enter or paste message content to analyze", "error");
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
  btnText.textContent = "Inspecting Threat Vectors...";

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
    showToast("Threat assessment compiled successfully", "success");

  } catch (err) {
    showToast(`Analysis Failed: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btnSpinner.classList.add("hidden");
    btnText.textContent = "Run Threat Analysis";
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
  conf.textContent = `Confidence: ${(data.confidence * 100).toFixed(0)}%`;
  stageBadge.textContent = data.stage_applied;
  latency.textContent = `${data.processing_time_ms.toFixed(1)} ms`;

  // Animate numeric score count up
  animateValue(scoreEl, 0, score, 600);

  // Circular SVG Gauge Animation
  const gaugeBar = document.getElementById("gauge-circle-bar");
  if (gaugeBar) {
    const radius = 42;
    const circumference = 2 * Math.PI * radius; // ~263.89
    gaugeBar.style.strokeDasharray = `${circumference} ${circumference}`;
    const offset = circumference - (score / 100) * circumference;
    gaugeBar.style.strokeDashoffset = offset;
  }

  // Tier Classification Styling & Icons
  banner.className = "assessment-banner flex flex-col sm:flex-row items-center justify-between gap-4 ";
  if (data.classification === "Likely Scam") {
    banner.classList.add("banner-scam");
    icon.className = "w-11 h-11 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-500 flex items-center justify-center";
    icon.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>`;
    subtitle.textContent = "High Scam Risk: Critical financial or credential compromise vector identified";
    if (gaugeBar) gaugeBar.style.stroke = "var(--threat-critical)";
  } else if (data.classification === "Suspicious") {
    banner.classList.add("banner-suspicious");
    icon.className = "w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-500 flex items-center justify-center";
    icon.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    subtitle.textContent = "Elevated Risk: Contains anomalous urgency, marketing claims, or unverified links";
    if (gaugeBar) gaugeBar.style.stroke = "var(--threat-medium)";
  } else if (data.classification === "Unable to Determine") {
    banner.classList.add("banner-undetermined");
    icon.className = "w-11 h-11 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-500 flex items-center justify-center";
    icon.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    subtitle.textContent = "Inconclusive: Text length or context is insufficient for high-confidence classification";
    if (gaugeBar) gaugeBar.style.stroke = "var(--threat-undetermined)";
  } else {
    banner.classList.add("banner-safe");
    icon.className = "w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 flex items-center justify-center";
    icon.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`;
    subtitle.textContent = "Benign Content: Consistent with normal interpersonal or transactional communication";
    if (gaugeBar) gaugeBar.style.stroke = "var(--threat-safe)";
  }

  // Redacted Text Preview Banner
  const redBox = document.getElementById("redacted-preview-box");
  const redText = document.getElementById("redacted-preview-text");
  if (data.pii_redacted && data.redacted_preview) {
    redBox.classList.remove("hidden");
    redText.textContent = data.redacted_preview;
  } else {
    redBox.classList.add("hidden");
  }

  // Truncation Warning Banner (Professor Feedback)
  const truncBox = document.getElementById("truncation-warning-box");
  const truncText = document.getElementById("truncation-warning-text");
  if (truncBox) {
    if (data.is_truncated) {
      truncBox.classList.remove("hidden");
      truncText.textContent = data.truncation_warning || "Notification preview appears clipped by Android. To ensure complete scam detection, submit the full unclipped message via Android Share Sheet or manual paste.";
    } else {
      truncBox.classList.add("hidden");
    }
  }

  // 1. Visual Threat Inspector (Annotated Message)
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

  // 2. Multidimensional Threat Vectors
  const vectorsGrid = document.getElementById("threat-vectors-grid");
  const primBadge = document.getElementById("primary-vector-badge");
  if (vectorsGrid) {
    vectorsGrid.innerHTML = "";
    const vectors = data.threat_vectors ? data.threat_vectors.scores : null;
    const ratings = data.threat_vectors ? data.threat_vectors.ratings : null;
    const prim = data.threat_vectors ? (data.threat_vectors.primary_vector || "None") : "None";

    if (primBadge) {
      primBadge.textContent = `Primary: ${prim.replace(/_/g, " ").toUpperCase()}`;
    }

    if (vectors) {
      Object.entries(vectors).forEach(([key, vScore]) => {
        const meta = VECTOR_META[key] || { label: key, icon: "•" };
        const rating = ratings ? (ratings[key] || "LOW") : "LOW";

        let barColor = "bg-emerald-500";
        let ratingBadge = "text-emerald-500 bg-emerald-500/10 border-emerald-500/20";
        if (rating === "CRITICAL") {
          barColor = "bg-rose-500";
          ratingBadge = "text-rose-500 bg-rose-500/10 border-rose-500/20";
        } else if (rating === "HIGH") {
          barColor = "bg-amber-500";
          ratingBadge = "text-amber-500 bg-amber-500/10 border-amber-500/20";
        } else if (rating === "MEDIUM") {
          barColor = "bg-yellow-500";
          ratingBadge = "text-yellow-500 bg-yellow-500/10 border-yellow-500/20";
        }

        const div = document.createElement("div");
        div.className = "p-3 rounded-xl soc-card-inset space-y-2";
        div.innerHTML = `
          <div class="flex items-center justify-between text-xs font-semibold">
            <span class="flex items-center gap-1.5 text-slate-800 dark:text-slate-200">
              <span class="text-indigo-500">${meta.icon}</span>
              <span>${meta.label}</span>
            </span>
            <div class="flex items-center gap-1.5">
              <span class="px-1.5 py-0.5 rounded text-[10px] font-bold border ${ratingBadge}">${rating}</span>
              <span class="font-mono text-[11px] text-slate-400">${vScore.toFixed(0)}%</span>
            </div>
          </div>
          <div class="vector-track">
            <div class="vector-bar ${barColor}" style="width: ${vScore}%"></div>
          </div>
        `;
        vectorsGrid.appendChild(div);
      });
    }
  }

  // 3. Domain Typosquatting & Threat Intelligence
  const urlCard = document.getElementById("url-intel-card");
  const urlDetails = document.getElementById("url-intel-details");
  if (urlCard && urlDetails) {
    const urls = (data.url_intelligence && data.url_intelligence.details) || [];
    if (urls.length > 0) {
      urlCard.classList.remove("hidden");
      urlDetails.innerHTML = urls.map(u => {
        const typosquatWarning = u.is_typosquat ? 
          `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-500 border border-rose-500/20">Typosquat Target: <strong>${u.typosquat_target}</strong> (Edit Distance: ${u.typosquat_distance})</span>` : "";
        const riskyTldWarning = u.risky_tld ? 
          `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20">Suspicious TLD: .${u.tld}</span>` : "";
        const entropyBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-[#151B26] text-slate-500">Entropy: ${u.entropy.toFixed(2)}</span>`;
        const shortenerBadge = u.is_shortener ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/10 text-purple-500 border border-purple-500/20">URL Shortener</span>` : "";

        return `
          <div class="p-3 rounded-xl soc-card-inset space-y-2 font-mono text-[11px]">
            <div class="flex items-center justify-between flex-wrap gap-1 font-bold text-slate-800 dark:text-slate-200">
              <span class="break-all text-indigo-500 dark:text-indigo-400">${u.raw_url}</span>
              <span class="px-2 py-0.5 rounded text-[10px] ${u.risk_score >= 50 ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'}">Domain Threat: ${u.risk_score.toFixed(0)}/100</span>
            </div>
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-slate-500 font-sans">Hostname: <strong>${u.domain}</strong></span>
              ${typosquatWarning}
              ${riskyTldWarning}
              ${entropyBadge}
              ${shortenerBadge}
            </div>
            ${u.risk_factors && u.risk_factors.length > 0 ? `<div class="text-[10px] text-rose-500 font-sans">Risk Factors: ${u.risk_factors.join(" • ")}</div>` : ''}
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
          ? "bg-rose-500/10 text-rose-500 border-rose-500/20"
          : "bg-emerald-500/10 text-emerald-500 border-emerald-500/20";
        const sign = isScam ? "+" : "";
        return `<span class="px-2 py-0.5 rounded font-mono border ${badgeColor}" title="Feature Weight: ${t.weight.toFixed(2)}">${t.token} <strong class="opacity-80">${sign}${t.weight.toFixed(1)}</strong></span>`;
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
      li.className = "flex items-start gap-2";
      li.innerHTML = `
        <svg class="w-4 h-4 text-indigo-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
        <span class="leading-relaxed">${act}</span>
      `;
      recList.appendChild(li);
    });
  }
}

// User Feedback
async function sendFeedback(label) {
  if (!state.currentRequestId) {
    showToast("No active inspection to rate", "error");
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
        user_notes: `Marked by analyst as ${label}`
      })
    });
    if (res.ok) {
      showToast("Feedback submitted to evaluation store", "success");
    }
  } catch (err) {
    showToast("Feedback submission failed", "error");
  }
}

// =========================================================================
// TAB 2: LIVE "WHAT-IF" SIMULATION SANDBOX
// =========================================================================
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
      document.getElementById("sandbox-score").innerHTML = `0<span class="text-xs font-normal opacity-70">/100</span>`;
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

      const banner = document.getElementById("sandbox-result-banner");
      banner.className = "assessment-banner flex items-center justify-between ";
      if (data.classification === "Likely Scam") {
        banner.classList.add("banner-scam");
      } else if (data.classification === "Suspicious") {
        banner.classList.add("banner-suspicious");
      } else {
        banner.classList.add("banner-safe");
      }

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
              <span class="flex items-center gap-1.5"><span class="text-indigo-500">${meta.icon}</span> ${meta.label}</span>
              <span class="font-mono">${score.toFixed(0)}%</span>
            </div>
            <div class="vector-track">
              <div class="vector-bar ${color}" style="width: ${score}%"></div>
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

// =========================================================================
// FORENSIC INVESTIGATION REPORT & EXPORT
// =========================================================================
async function openForensicReportModal() {
  if (!state.currentText) {
    showToast("Please inspect a message first to generate a threat report", "error");
    return;
  }

  const modal = document.getElementById("forensic-report-modal");
  const modalContent = document.getElementById("modal-report-content");
  modalContent.innerHTML = `<div class="p-8 text-center text-slate-400"><span class="spinner-ring"></span> Compiling Forensic Artifacts & IOCs...</div>`;
  modal.classList.add("open");

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
        <div class="soc-card-inset p-3.5 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Investigation Time</span>
            <span class="font-mono text-slate-800 dark:text-slate-200">${rep.timestamp_utc}</span>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Verdict</span>
            <span class="font-bold ${rep.classification === 'Likely Scam' ? 'text-rose-500' : 'text-emerald-500'}">${rep.classification} (${rep.risk_score.toFixed(0)}/100)</span>
          </div>
          <div>
            <span class="text-slate-400 block text-[10px] uppercase font-bold">Primary Threat Vector</span>
            <span class="font-semibold text-slate-800 dark:text-slate-200">${(rep.primary_threat_vector || "None").replace(/_/g, " ").toUpperCase()}</span>
          </div>
        </div>

        <div>
          <span class="text-slate-400 block text-[10px] uppercase font-bold mb-1">SHA-256 Message Cryptographic Hash</span>
          <div class="p-2 soc-card-inset font-mono text-[11px] break-all select-all text-slate-700 dark:text-slate-300">
            ${rep.message_hash_sha256}
          </div>
        </div>

        <div>
          <span class="text-slate-400 block text-[10px] uppercase font-bold mb-1">Indicators of Compromise (IOCs)</span>
          ${rep.indicators_of_compromise && rep.indicators_of_compromise.length > 0 ? `
            <div class="soc-card-inset overflow-hidden">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-100 dark:bg-[#151B26] text-slate-500 text-[10px] uppercase font-semibold">
                  <tr>
                    <th class="px-3 py-1.5">Type</th>
                    <th class="px-3 py-1.5">Artifact / Value</th>
                    <th class="px-3 py-1.5">Risk</th>
                    <th class="px-3 py-1.5">Forensic Notes</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-[#1C2433] font-mono text-[11px]">
                  ${rep.indicators_of_compromise.map(ioc => `
                    <tr>
                      <td class="px-3 py-1.5 text-indigo-500 font-sans text-[10px]">${ioc.type}</td>
                      <td class="px-3 py-1.5 text-slate-800 dark:text-slate-200 break-all">${ioc.value}</td>
                      <td class="px-3 py-1.5 font-bold ${ioc.risk_score >= 50 ? 'text-rose-500' : 'text-slate-400'}">${ioc.risk_score.toFixed(0)}</td>
                      <td class="px-3 py-1.5 text-slate-400 font-sans text-[10px]">${ioc.notes}</td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          ` : `<div class="text-xs text-slate-400 italic p-3 soc-card-inset">No specific indicators or malicious domains extracted.</div>`}
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
    modalContent.innerHTML = `<div class="p-4 bg-rose-500/10 text-rose-500 rounded-xl text-xs">Error generating report: ${err.message}</div>`;
  }
}

function closeForensicReportModal() {
  const modal = document.getElementById("forensic-report-modal");
  if (modal) modal.classList.remove("open");
}

function exportReportJSON() {
  if (!state.currentDetectionData) {
    showToast("Please inspect a message first before exporting JSON", "error");
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
  showToast("JSON report downloaded", "success");
}

// =========================================================================
// RESEARCH BENCHMARK & AUDIT HISTORY
// =========================================================================
async function loadBenchmarkData() {
  try {
    const res = await fetch(`${state.apiBase}/benchmark`);
    if (!res.ok) return;
    const data = await res.json();
    if (!data.models) return;

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
      if (isSelected) tr.className = "bg-indigo-500/10 font-semibold";

      tr.innerHTML = `
        <td class="px-5 py-3 font-medium text-slate-900 dark:text-slate-100">${modelNames[key] || key}</td>
        <td class="px-4 py-3 text-center font-mono">${(m.accuracy * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.precision * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.recall * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${(m.f1_score * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-rose-500">${(m.false_positive_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono text-amber-500">${(m.false_negative_rate * 100).toFixed(2)}%</td>
        <td class="px-4 py-3 text-center font-mono">${m.backend_requests} / ${data.test_samples}</td>
        <td class="px-4 py-3 text-center font-mono text-indigo-500 dark:text-indigo-400 font-bold">${m.request_reduction_pct.toFixed(1)}%</td>
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
        <td class="px-4 py-3"><span class="px-2 py-0.5 rounded text-[10px] font-mono border">${item.classification}</span></td>
        <td class="px-4 py-3 font-mono font-semibold">${item.risk_score.toFixed(0)}</td>
        <td class="px-4 py-3 font-mono text-slate-400">${item.latency_ms.toFixed(1)} ms</td>
        <td class="px-4 py-3 font-mono text-[10px] text-slate-400">${item.request_id.substring(0, 8)}...</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("History load error", err);
  }
}

async function clearAuditHistory() {
  try {
    const res = await fetch(`${state.apiBase}/history`, {
      method: "DELETE",
      headers: { "X-Session-ID": state.sessionId }
    });
    if (res.ok) {
      showToast("Session audit history cleared", "info");
      loadAuditHistory();
    }
  } catch (err) {
    showToast("Failed to clear history: " + err.message, "error");
  }
}

// =========================================================================
// TAB 4: BATCH TRAFFIC REDUCTION EVALUATOR
// =========================================================================
function loadBatchPreset() {
  const area = document.getElementById("batch-input");
  if (area) area.value = BATCH_PRESET.join("\n");
}

async function runBatchEvaluation() {
  const area = document.getElementById("batch-input");
  const raw = area ? area.value.trim() : "";
  if (!raw) {
    showToast("Please enter batch messages to evaluate", "error");
    return;
  }
  const messages = raw.split("\n").map(m => m.trim()).filter(m => m.length > 0);
  if (messages.length === 0) return;

  const container = document.getElementById("batch-results-container");
  container.classList.remove("hidden");
  container.innerHTML = `<div class="p-8 soc-card text-center text-slate-400"><span class="spinner-ring"></span> Executing Stage 1 edge vs Stage 2 cloud benchmark...</div>`;

  try {
    const res = await fetch(`${state.apiBase}/evaluate-batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages, use_prefilter: true })
    });
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    container.innerHTML = `
      <div class="soc-card p-5 grid grid-cols-1 sm:grid-cols-4 gap-4 text-center">
        <div>
          <span class="text-xs text-slate-500 block font-medium">Total Messages</span>
          <span class="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100">${data.total_messages}</span>
        </div>
        <div>
          <span class="text-xs text-emerald-500 block font-medium">Filtered On-Device</span>
          <span class="text-2xl font-bold font-mono text-emerald-500">${data.filtered_locally}</span>
        </div>
        <div>
          <span class="text-xs text-amber-500 block font-medium">Routed to Cloud</span>
          <span class="text-2xl font-bold font-mono text-amber-500">${data.routed_to_backend}</span>
        </div>
        <div>
          <span class="text-xs text-indigo-500 block font-medium">Traffic Saved</span>
          <span class="text-2xl font-bold font-mono text-indigo-500">${data.request_reduction_pct}%</span>
        </div>
      </div>
      <div class="soc-card p-4 overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-50 dark:bg-[#151B26] text-slate-500 uppercase font-semibold">
            <tr>
              <th class="px-4 py-2">Message Snippet</th>
              <th class="px-4 py-2">Routing Decision</th>
              <th class="px-4 py-2">Classification</th>
              <th class="px-4 py-2">Risk Score</th>
              <th class="px-4 py-2">Latency</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-[#1C2433] font-mono text-[11px]">
            ${data.results.map(r => `
              <tr>
                <td class="px-4 py-2 text-slate-700 dark:text-slate-200 font-sans text-xs">${r.text_snippet}</td>
                <td class="px-4 py-2 font-semibold ${r.prefilter_routed ? 'text-amber-500' : 'text-emerald-500'}">${r.prefilter_routed ? 'Routed to Cloud' : 'Filtered on Device'}</td>
                <td class="px-4 py-2 text-slate-800 dark:text-slate-200">${r.classification}</td>
                <td class="px-4 py-2 text-slate-800 dark:text-slate-200">${r.risk_score.toFixed(0)}</td>
                <td class="px-4 py-2 text-slate-400">${r.processing_time_ms.toFixed(1)} ms</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;

    showToast("Batch traffic benchmark complete", "success");

  } catch (err) {
    container.innerHTML = `<div class="p-4 bg-rose-500/10 text-rose-500 rounded-xl text-xs">Error: ${err.message}</div>`;
  }
}

// =========================================================================
// Thesis Committee Defense: Scalability Simulator & Preset Scenarios
// =========================================================================

function updateScalabilitySim() {
  const usersEl = document.getElementById("sim-users");
  const rateEl = document.getElementById("sim-rate");
  if (!usersEl || !rateEl) return;

  const users = parseInt(usersEl.value, 10);
  const rate = parseInt(rateEl.value, 10);

  document.getElementById("sim-users-val").textContent = `${users.toLocaleString()} users`;
  document.getElementById("sim-rate-val").textContent = `${rate} notifs/min`;

  // Total raw incoming notifications across users
  const rawRpm = users * rate;
  const rawRph = rawRpm * 60;

  // Naive streaming: all raw notifications hit the cloud
  document.getElementById("sim-naive-rpm").textContent = `${rawRpm.toLocaleString()} req/min`;
  document.getElementById("sim-naive-rph").textContent = `${rawRph.toLocaleString()} req/hour`;

  // ScamGuard Two-Stage Filtering:
  // 1. Noise Filter drops ~85% of notifications (Meesho, Amazon, Flipkart, weather, social likes) locally
  // 2. Local Edge Prefilter evaluates remaining 15% communication messages and keeps 89.96% of benign chats on device
  const commNotifsRpm = rawRpm * 0.15; // 85% noise dropped
  const cloudRpm = commNotifsRpm * (1.0 - 0.8996); // ~10% of comm notifs routed
  const cloudRph = cloudRpm * 60;

  document.getElementById("sim-scamguard-rpm").textContent = `${cloudRpm < 1 ? cloudRpm.toFixed(1) : Math.round(cloudRpm).toLocaleString()} req/min`;
  document.getElementById("sim-scamguard-rph").textContent = `${Math.round(cloudRph).toLocaleString()} req/hour`;
}

function loadDefensePreset(type) {
  const input = document.getElementById("message-input");
  if (!input) return;

  switch (type) {
    case "truncated":
      input.value = "Chase Bank: Unauthorized login attempt from unfamiliar device. To safeguard your account, click http://chase-login-resolve.xyz/ver...";
      break;
    case "meesho":
      input.value = "Meesho Deal: 70% OFF Kurtis & Sarees starting at Rs. 149! Free delivery on first order. Open Meesho app now.";
      break;
    case "instagram":
      input.value = "alex_smith liked your story. See what else they shared today on Instagram.";
      break;
    case "friend_chat":
      input.value = "Hey! Can you send me the lecture slides from today's meeting with Haider sir?";
      break;
  }

  // Switch to detector tab and run analysis
  switchTab("detector");
  analyzeMessage();
}

async function runLiveFloodTest() {
  const btn = document.getElementById("btn-run-flood-test");
  const panel = document.getElementById("flood-metrics-panel");
  const container = document.getElementById("flood-results-container");

  if (!btn) return;
  btn.disabled = true;
  btn.innerHTML = `<span>⏳</span><span>Processing 200 Events...</span>`;

  try {
    const whatsappSamples = [
      "Hey! Are you still free for dinner tonight?",
      "URGENT: Chase Bank alert! Account suspended. Verify at https://chase-security-verify.xyz immediately.",
      "Can you send me the lecture notes from today?",
      "Your verification code is 492810. Do not share with anyone.",
      "Sounds good, see you later!"
    ];

    const telegramMessages = [
      "Winner! You won the UK Lottery! Claim your £500,000 jackpot now.",
      "Hey, let's meet at 5pm outside.",
      "SECURITY NOTICE: Wells Fargo account suspended. Visit http://192.168.1.10/verify.",
      "Thanks for sharing the document.",
      "Claim your free $500 gift card at bit.ly/free-gift-promo"
    ];

    const messages = [];
    const packages = [];

    // Generate 100 from WhatsApp and 100 from Telegram = 200 total concurrent notifications
    for (let i = 0; i < 20; i++) {
      for (const m of whatsappSamples) {
        messages.push(m);
        packages.push("com.whatsapp");
      }
      for (const m of telegramMessages) {
        messages.push(m);
        packages.push("org.telegram.messenger");
      }
    }

    const res = await fetch(`${state.apiBase}/detect/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: messages,
        source: "NOTIFICATION",
        app_packages: packages
      })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to execute batch test`);
    const data = await res.json();

    panel.classList.remove("hidden");
    container.classList.remove("hidden");

    document.getElementById("flood-count").textContent = `${data.total_processed} / 200`;
    document.getElementById("flood-latency").textContent = `${data.total_latency_ms.toFixed(1)} ms`;
    document.getElementById("flood-avg-latency").textContent = `${data.avg_latency_ms.toFixed(2)} ms`;
    document.getElementById("flood-throughput").textContent = `${data.throughput_items_per_sec.toLocaleString()} msg/s`;

    container.innerHTML = `
      <table class="w-full text-left">
        <thead class="bg-slate-100 dark:bg-slate-800/80 text-[10px] font-mono text-slate-500 uppercase sticky top-0">
          <tr>
            <th class="px-3 py-1.5">#</th>
            <th class="px-3 py-1.5">Package</th>
            <th class="px-3 py-1.5">Snippet</th>
            <th class="px-3 py-1.5">Classification</th>
            <th class="px-3 py-1.5">Risk</th>
            <th class="px-3 py-1.5">Latency</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
          ${data.results.map((r, i) => `
            <tr class="${i % 2 === 0 ? 'bg-transparent' : 'bg-slate-50/50 dark:bg-slate-800/30'}">
              <td class="px-3 py-1 text-slate-400">${i + 1}</td>
              <td class="px-3 py-1 text-indigo-400">${r.package_name || 'msg'}</td>
              <td class="px-3 py-1 text-slate-700 dark:text-slate-300 font-sans">${r.text_snippet}</td>
              <td class="px-3 py-1 font-bold ${r.classification === 'Likely Scam' ? 'text-rose-500' : (r.classification === 'Suspicious' ? 'text-amber-500' : 'text-emerald-500')}">${r.classification}</td>
              <td class="px-3 py-1">${r.risk_score.toFixed(0)}</td>
              <td class="px-3 py-1 text-slate-400">${r.processing_time_ms.toFixed(1)}ms</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;

    showToast(`Processed 200 events in ${data.total_latency_ms.toFixed(1)}ms (${data.throughput_items_per_sec} msg/sec)`, "success");

  } catch (err) {
    showToast(`Flood test error: ${err.message}`, "error");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>⚡</span><span>Execute 200-Event Flood Test</span>`;
  }
}
