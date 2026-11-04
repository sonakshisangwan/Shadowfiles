/**
 * =============================================================================
 * REGEX DETECTIVE // SHADOWFILES - CLIENT GAME ENGINE
 * High-tech Cybercrime Forensic Puzzle Game Controller
 * =============================================================================
 */

// Global Game State
const gameState = {
  currentCaseId: "case_01",
  activeCaseData: null,
  allCases: [],
  player: {
    name: "Inspector Sonakshi",
    reputation: 100,
    coins: 50,
    score: 0,
    solved_cases: [],
    failed_cases: [],
    case_scores: {},
  },
  selectedSuspect: null,
  audioEnabled: true,
  crtEnabled: true,
  sandboxMode: false, // false = progressive story unlock; true = all unlocked
  audioContext: null,
};

// =============================================================================
// 1. PROCEDURAL SOUND ENGINE (Web Audio API - Zero External Dependencies)
// =============================================================================
function initAudio() {
  if (!gameState.audioContext) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    if (AudioCtx) {
      gameState.audioContext = new AudioCtx();
    }
  }
}

function playSfx(type) {
  if (!gameState.audioEnabled) return;
  try {
    initAudio();
    if (!gameState.audioContext) return;
    if (gameState.audioContext.state === "suspended") {
      gameState.audioContext.resume();
    }

    const ctx = gameState.audioContext;
    const now = ctx.currentTime;

    switch (type) {
      case "click": {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.04);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
        break;
      }

      case "scan": {
        // High-tech sci-fi scanner frequency sweep
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.linearRampToValueAtTime(960, now + 0.22);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.26);
        break;
      }

      case "clue": {
        // Double-bell major chime (C5 -> G5)
        [523.25, 783.99].forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const start = now + i * 0.1;
          osc.type = "sine";
          osc.frequency.setValueAtTime(freq, start);
          gain.gain.setValueAtTime(0.18, start);
          gain.gain.exponentialRampToValueAtTime(0.001, start + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(start);
          osc.stop(start + 0.36);
        });
        break;
      }

      case "error": {
        // Low glitch saw-tooth alert
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.linearRampToValueAtTime(80, now + 0.22);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.22);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.24);
        break;
      }

      case "victory": {
        // Triumphant 4-note victory arpeggio (C5 -> E5 -> G5 -> C6)
        [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const start = now + idx * 0.12;
          osc.type = "triangle";
          osc.frequency.setValueAtTime(freq, start);
          gain.gain.setValueAtTime(0.25, start);
          gain.gain.exponentialRampToValueAtTime(0.001, start + 0.45);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(start);
          osc.stop(start + 0.48);
        });
        break;
      }

      case "defeat": {
        // Descending defeat minor tone
        [392.0, 311.13, 261.63].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const start = now + idx * 0.15;
          osc.type = "sawtooth";
          osc.frequency.setValueAtTime(freq, start);
          gain.gain.setValueAtTime(0.18, start);
          gain.gain.exponentialRampToValueAtTime(0.001, start + 0.35);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(start);
          osc.stop(start + 0.38);
        });
        break;
      }
    }
  } catch (e) {
    console.warn("Audio playback non-critical error:", e);
  }
}

function toggleAudio() {
  gameState.audioEnabled = !gameState.audioEnabled;
  localStorage.setItem("regex_audio", gameState.audioEnabled ? "1" : "0");
  updateAudioUi();
  playSfx("click");
}

function updateAudioUi() {
  const icon = gameState.audioEnabled ? "🔊" : "🔇";
  const label = gameState.audioEnabled ? "SFX: ON" : "SFX: OFF";

  const startText = document.getElementById("startAudioStatusText");
  if (startText) startText.textContent = label;

  const hudIcon = document.getElementById("hudAudioIcon");
  if (hudIcon) hudIcon.textContent = icon;
}

// =============================================================================
// 2. SCREEN VIEW MANAGEMENT
// =============================================================================
function switchScreen(screenName) {
  playSfx("click");
  const screens = {
    start: document.getElementById("startScreen"),
    map: document.getElementById("mapScreen"),
    game: document.getElementById("gameScreen"),
  };

  Object.entries(screens).forEach(([key, screenEl]) => {
    if (screenEl) {
      if (key === screenName) {
        screenEl.classList.add("active");
        screenEl.style.display = "block";
      } else {
        screenEl.classList.remove("active");
        screenEl.style.display = "none";
      }
    }
  });

  window.scrollTo({ top: 0, behavior: "smooth" });

  if (screenName === "map") {
    renderMissionMap();
  } else if (screenName === "start") {
    updateStartDossier();
  }
}

// =============================================================================
// 3. PLAYER & CAREER DOSSIER MANAGEMENT
// =============================================================================
async function syncPlayerProfile() {
  try {
    const res = await fetch("/player");
    if (!res.ok) return;
    const data = await res.json();
    if (data.success && data.player) {
      gameState.player = data.player;
      updateStartDossier();
      updateHudProfile();
    }
  } catch (err) {
    console.error("Failed to sync player profile:", err);
  }
}

function calculateDetectiveRank(score) {
  if (score >= 1200) return "Apex Cybercrime Bureau Chief";
  if (score >= 750) return "Senior Cryptographic Sleuth";
  if (score >= 350) return "Field Cyber Forensics Detective";
  return "Junior Cyber Intelligence Agent";
}

function updateStartDossier() {
  const p = gameState.player;
  const nameEl = document.getElementById("startPlayerName");
  const rankEl = document.getElementById("startPlayerRank");
  const scoreEl = document.getElementById("startTotalScore");
  const repEl = document.getElementById("startReputation");
  const repBarEl = document.getElementById("startReputationBar");
  const coinsEl = document.getElementById("startCoins");
  const solvedEl = document.getElementById("startSolvedCount");
  const ratioEl = document.getElementById("startClearedRatio");

  if (nameEl) nameEl.textContent = p.name || "Inspector Detective";
  if (rankEl) rankEl.textContent = calculateDetectiveRank(p.score || 0);
  if (scoreEl) scoreEl.textContent = (p.score || 0).toLocaleString();
  if (repEl) repEl.textContent = `${p.reputation ?? 100}%`;
  if (repBarEl) repBarEl.style.width = `${p.reputation ?? 100}%`;
  if (coinsEl) coinsEl.textContent = `🪙 ${p.coins ?? 50}`;

  const solvedCount = (p.solved_cases || []).length;
  if (solvedEl) solvedEl.textContent = `${solvedCount} / 8`;
  if (ratioEl) ratioEl.textContent = `${Math.round((solvedCount / 8) * 100)}% Cleared`;
}

function updateHudProfile() {
  const p = gameState.player;
  const repCountEl = document.getElementById("hudReputationCount");
  const repFillEl = document.getElementById("hudReputationFill");
  const coinsEl = document.getElementById("hudCoins");
  const scoreEl = document.getElementById("hudScore");

  const rep = p.reputation ?? 100;
  if (repCountEl) repCountEl.textContent = `${rep}%`;
  if (repFillEl) {
    repFillEl.style.width = `${rep}%`;
    if (rep < 25) {
      repFillEl.classList.add("danger");
    } else {
      repFillEl.classList.remove("danger");
    }
  }

  if (coinsEl) coinsEl.textContent = p.coins ?? 50;
  if (scoreEl) scoreEl.textContent = (p.score || 0).toLocaleString();
}

// =============================================================================
// 4. MISSION MAP & PROGRESSION
// =============================================================================
async function fetchAllCases() {
  try {
    const res = await fetch("/cases");
    if (!res.ok) return;
    const data = await res.json();
    if (data.success && data.cases) {
      gameState.allCases = data.cases;
      if (data.player) gameState.player = data.player;
      renderMissionMap();
    }
  } catch (err) {
    console.error("Failed to load cases catalog:", err);
  }
}

function isCaseUnlocked(caseId, index) {
  if (gameState.sandboxMode) return true;
  if (index === 0) return true; // Case 01 always unlocked

  // Normal progression: case N is unlocked if previous case is solved
  const prevCase = gameState.allCases[index - 1];
  if (!prevCase) return true;
  return (gameState.player.solved_cases || []).includes(prevCase.case_id);
}

function renderMissionMap() {
  const grid = document.getElementById("missionCardsGrid");
  if (!grid || !gameState.allCases.length) return;

  const solvedSet = new Set(gameState.player.solved_cases || []);
  const solvedCount = solvedSet.size;
  const totalCount = gameState.allCases.length;
  const percent = Math.round((solvedCount / totalCount) * 100);

  // Update progress bar
  const progressLabel = document.getElementById("mapProgressLabel");
  const progressBar = document.getElementById("mapProgressBar");
  if (progressLabel) progressLabel.textContent = `${solvedCount} / ${totalCount} Operations Concluded (${percent}%)`;
  if (progressBar) progressBar.style.width = `${percent}%`;

  grid.innerHTML = "";

  gameState.allCases.forEach((c, idx) => {
    const isUnlocked = isCaseUnlocked(c.case_id, idx);
    const isSolved = solvedSet.has(c.case_id);
    const isActive = gameState.currentCaseId === c.case_id;
    const isBoss = c.case_id === "case_08";

    const card = document.createElement("div");
    card.className = `stage-card ${isBoss ? "boss-stage" : ""} ${
      isActive ? "active-stage" : ""
    } ${isSolved ? "cleared-stage" : ""} ${!isUnlocked ? "locked-stage" : ""}`;

    // Badge styling
    let badgeHtml = "";
    if (isSolved) {
      badgeHtml = '<span class="stage-badge badge-cleared">✓ CLEARED</span>';
    } else if (isUnlocked) {
      badgeHtml = '<span class="stage-badge badge-available">● AVAILABLE</span>';
    } else {
      badgeHtml = '<span class="stage-badge badge-locked">🔒 LOCKED</span>';
    }

    // Stars
    const score = gameState.player.case_scores[c.case_id] || 0;
    const starsCount = isSolved ? 3 : score > 0 ? 1 : 0;
    const starsString = "★".repeat(starsCount) + "☆".repeat(3 - starsCount);

    card.innerHTML = `
      <div class="stage-top-meta">
        <span class="stage-number">STAGE 0${idx + 1}</span>
        ${badgeHtml}
      </div>
      <h3 class="stage-title">${escapeHtml(c.title)}</h3>
      <p class="stage-desc">
        ${isBoss ? "👑 Apex Syndicate Vault • Penetrate 4 cryptographic security chambers." : `Difficulty: ${escapeHtml(c.difficulty)} • Budget: ${c.search_budget} Warrants`}
      </p>
      <div class="stage-footer-meta">
        <span class="stage-stars">${starsString}</span>
        <span class="stage-score-val">${score ? `${score} pts` : "Unsolved"}</span>
      </div>
      <button class="game-btn ${isUnlocked ? (isBoss ? 'btn-warrant' : 'btn-primary') : 'btn-secondary'}" 
              style="width: 100%; margin-top: 8px;" 
              ${!isUnlocked ? "disabled" : ""}>
        <span>${isUnlocked ? "DEPLOY AGENT 🔍" : "LOCKED"}</span>
      </button>
    `;

    if (isUnlocked) {
      card.addEventListener("click", () => {
        loadCase(c.case_id);
        switchScreen("game");
      });
    }

    grid.appendChild(card);
  });
}

// =============================================================================
// 5. CASE LOADING & INVESTIGATION CONTROLLER
// =============================================================================
async function loadCase(caseId) {
  gameState.currentCaseId = caseId;
  gameState.selectedSuspect = null;
  clearTerminalFeedback();
  hideVerdictBox();

  try {
    const res = await fetch(`/case/${caseId}`);
    if (!res.ok) {
      showToast(`Error loading case: ${res.statusText}`, "error");
      return;
    }

    const data = await res.json();
    if (!data.success) {
      showToast(data.message || "Failed to load case.", "error");
      return;
    }

    gameState.activeCaseData = data;
    renderInvestigationView(data);
    fetchCaseNotes(caseId);
  } catch (err) {
    showToast(`Network error loading case: ${err}`, "error");
  }
}

function renderInvestigationView(data) {
  // HUD Update
  const hudCaseId = document.getElementById("hudCaseId");
  const hudCaseTitle = document.getElementById("hudCaseTitle");
  if (hudCaseId) hudCaseId.textContent = data.case_id.toUpperCase().replace("_", " ");
  if (hudCaseTitle) hudCaseTitle.textContent = data.title;

  // Warrant Energy Cells
  updateWarrantEnergyMeter(data.remaining_budget, data.search_budget);

  // Panel Header
  const panelCaseTitle = document.getElementById("panelCaseTitle");
  const panelCaseDiff = document.getElementById("panelCaseDiff");
  const panelCaseStatus = document.getElementById("panelCaseStatus");
  const panelBriefingText = document.getElementById("panelBriefingText");

  if (panelCaseTitle) panelCaseTitle.textContent = data.title;
  if (panelCaseDiff) panelCaseDiff.textContent = data.difficulty;
  if (panelCaseStatus) {
    const isSolved = (gameState.player.solved_cases || []).includes(data.case_id);
    panelCaseStatus.textContent = isSolved ? "CLEARED" : "IN PROGRESS";
    panelCaseStatus.style.color = isSolved ? "var(--green-neon)" : "var(--cyan-neon)";
  }
  if (panelBriefingText) panelBriefingText.textContent = data.briefing;

  // Vedic Vault Specialized Matrix (Case 08)
  const matrixContainer = document.getElementById("vaultChambersMatrix");
  if (data.vault_status && matrixContainer) {
    matrixContainer.style.display = "block";
    renderVaultMatrix(data.vault_status);
  } else if (matrixContainer) {
    matrixContainer.style.display = "none";
  }

  // Evidence Stream Box
  const evidenceBox = document.getElementById("evidenceBox");
  if (evidenceBox) evidenceBox.textContent = data.evidence_text || "No evidence records intercepted.";

  // Clues & Suspects
  renderClueInventory(data.collected_clues || []);
  renderSuspectsLineup(data.suspects || []);

  // Update HUD Reputation and Coins
  if (typeof data.player_reputation !== "undefined") {
    gameState.player.reputation = data.player_reputation;
  }
  if (typeof data.player_coins !== "undefined") {
    gameState.player.coins = data.player_coins;
  }
  updateHudProfile();
}

function updateWarrantEnergyMeter(remaining, total) {
  const countEl = document.getElementById("hudWarrantCount");
  const cellsEl = document.getElementById("hudEnergyCells");
  const searchBtn = document.getElementById("searchBtn");

  if (countEl) countEl.textContent = `${remaining} / ${total}`;
  if (cellsEl) {
    cellsEl.innerHTML = "";
    const max = Math.max(total, remaining);
    for (let i = 0; i < max; i++) {
      const cell = document.createElement("div");
      cell.className = `energy-cell ${i >= remaining ? "spent" : ""}`;
      cellsEl.appendChild(cell);
    }
  }

  if (searchBtn) {
    searchBtn.disabled = remaining <= 0;
  }
}

function renderVaultMatrix(v) {
  const progressText = document.getElementById("vaultBreachProgress");
  const grid = document.getElementById("vaultChambersGrid");
  if (!grid) return;

  if (progressText) {
    progressText.textContent = `${v.layers_unlocked} / ${v.total_layers} Chambers Breached (${v.percentage}%)`;
  }

  grid.innerHTML = "";
  Object.entries(v.chambers).forEach(([chamberName, isUnlocked]) => {
    const tile = document.createElement("div");
    tile.className = `vault-chamber-tile ${isUnlocked ? "unlocked" : ""}`;
    tile.innerHTML = `
      <div class="chamber-seal-icon">${isUnlocked ? "🔓" : "🔒"}</div>
      <div class="chamber-info">
        <span class="chamber-name">${escapeHtml(chamberName)}</span>
        <span class="chamber-status-tag">${isUnlocked ? "BREACHED" : "SEALED"}</span>
      </div>
    `;
    grid.appendChild(tile);
  });
}

function renderClueInventory(clues) {
  const tray = document.getElementById("clueInventoryTray");
  const badge = document.getElementById("clueCountBadge");
  if (!tray) return;

  if (badge) badge.textContent = `${clues.length} Clues Secured`;
  tray.innerHTML = "";

  if (!clues || clues.length === 0) {
    tray.innerHTML = `
      <div class="clue-slot-empty">
        <span>No forensic clues verified yet. Issue a warrant pattern above!</span>
      </div>
    `;
    return;
  }

  clues.forEach((clue) => {
    let icon = "🔍";
    if (clue.startsWith("+91") || clue.includes("-")) icon = "📱";
    if (clue.includes("@")) icon = "💳";
    if (clue.includes(":") || clue.includes("2026")) icon = "⏰";
    if (clue.startsWith("VAULT") || clue.includes("KEY")) icon = "🔑";

    const card = document.createElement("div");
    card.className = "clue-item-card";
    card.innerHTML = `
      <span class="clue-icon">${icon}</span>
      <span class="clue-text">${escapeHtml(clue)}</span>
    `;
    tray.appendChild(card);
  });
}

function renderSuspectsLineup(suspects) {
  const lineup = document.getElementById("suspectsLineup");
  if (!lineup) return;
  lineup.innerHTML = "";

  if (!suspects || suspects.length === 0) {
    lineup.innerHTML = '<p style="color: var(--text-dim); padding: 12px;">No suspects on docket.</p>';
    return;
  }

  const avatars = ["🕵️", "💼", "👤", "🕶️", "🎩"];

  suspects.forEach((suspect, idx) => {
    const card = document.createElement("div");
    card.className = "suspect-card";
    card.dataset.suspect = suspect;

    const avatar = avatars[idx % avatars.length];

    card.innerHTML = `
      <div class="suspect-avatar">${avatar}</div>
      <div class="suspect-meta">
        <span class="suspect-name">${escapeHtml(suspect)}</span>
        <span class="suspect-role">Person of Interest #${idx + 1}</span>
      </div>
    `;

    card.addEventListener("click", () => {
      document.querySelectorAll(".suspect-card").forEach((c) => c.classList.remove("selected"));
      card.classList.add("selected");
      gameState.selectedSuspect = suspect;
      playSfx("click");
    });

    lineup.appendChild(card);
  });
}

// =============================================================================
// 6. REGEX SEARCH EXECUTION & HIGHLIGHTING
// =============================================================================
function highlightMatches(matches) {
  const box = document.getElementById("evidenceBox");
  if (!box || !gameState.activeCaseData) return;

  const raw = gameState.activeCaseData.evidence_text || "";
  if (!matches || matches.length === 0) {
    box.textContent = raw;
    return;
  }

  let escaped = escapeHtml(raw);
  const uniqueMatches = Array.from(new Set(matches)).sort((a, b) => b.length - a.length);

  uniqueMatches.forEach((m) => {
    if (!m) return;
    const escapedMatch = escapeHtml(m);
    const regexSafe = new RegExp(escapedMatch.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&"), "g");
    escaped = escaped.replace(regexSafe, `<mark class="match-glow">${escapedMatch}</mark>`);
  });

  box.innerHTML = escaped;
}

async function executeWarrant() {
  const input = document.getElementById("regexInput");
  const pattern = input ? input.value.trim() : "";

  if (!pattern) {
    showToast("Please specify a regex pattern to execute warrant.", "warning");
    playSfx("error");
    triggerScreenShake();
    return;
  }

  const searchBtn = document.getElementById("searchBtn");
  if (searchBtn) {
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span class="icon">⚡</span><span>SCANNING...</span>';
  }

  playSfx("scan");

  try {
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: gameState.currentCaseId,
        pattern: pattern,
      }),
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      playSfx("error");
      triggerScreenShake();
      showToast(data.message || "Warrant execution failed.", "error");
      logTerminalDiagnostic(data.message || "Search failed.", "error");

      if (typeof data.remaining_budget !== "undefined") {
        updateWarrantEnergyMeter(data.remaining_budget, gameState.activeCaseData.search_budget);
      }
      return;
    }

    // Update remaining budget
    updateWarrantEnergyMeter(data.remaining_budget, gameState.activeCaseData.search_budget);

    // Highlight matches in evidence
    highlightMatches(data.matches);

    // Update inventory
    const prevCount = (gameState.activeCaseData.collected_clues || []).length;
    gameState.activeCaseData.collected_clues = data.collected_clues;
    renderClueInventory(data.collected_clues);

    if (data.collected_clues.length > prevCount) {
      playSfx("clue");
      showToast(`+${data.collected_clues.length - prevCount} new forensic clue(s) verified!`, "success");
    } else if (data.matches.length > 0) {
      playSfx("click");
    } else {
      playSfx("error");
    }

    // Update Scores
    gameState.player.score = data.total_score || gameState.player.score;
    if (typeof data.player_reputation !== "undefined") {
      gameState.player.reputation = data.player_reputation;
    }
    if (typeof data.player_coins !== "undefined") {
      gameState.player.coins = data.player_coins;
    }
    updateHudProfile();

    // Diagnostics & Metrics Readout
    displayTerminalMetrics(data);
  } catch (err) {
    playSfx("error");
    triggerScreenShake();
    showToast(`Warrant execution exception: ${err}`, "error");
    logTerminalDiagnostic(`Exception: ${err}`, "error");
  } finally {
    if (searchBtn) {
      const remaining = gameState.activeCaseData ? gameState.activeCaseData.remaining_budget : 1;
      searchBtn.disabled = remaining <= 0;
      searchBtn.innerHTML = '<span class="icon">🔍</span><span class="btn-text">ISSUE WARRANT</span>';
    }
  }
}

function displayTerminalMetrics(data) {
  const diagLog = document.getElementById("diagnosticsLog");
  const metricsPanel = document.getElementById("diagnosticsMetrics");
  const precisionFill = document.getElementById("metricPrecisionFill");
  const precisionVal = document.getElementById("metricPrecisionVal");
  const recallFill = document.getElementById("metricRecallFill");
  const recallVal = document.getElementById("metricRecallVal");
  const starsVal = document.getElementById("metricStarsVal");
  const scoreVal = document.getElementById("metricScoreVal");

  if (diagLog) {
    let msgClass = "success-msg";
    if (data.false_matches && data.false_matches.length > 0) msgClass = "error-msg";
    if (data.matches.length === 0) msgClass = "dim";

    diagLog.innerHTML = `<span class="${msgClass}">&gt; ${escapeHtml(data.feedback || "Scan completed.")}</span>`;
  }

  if (metricsPanel) {
    metricsPanel.style.display = "flex";
    const prec = Math.round((data.precision || 0) * 100);
    const rec = Math.round((data.recall || 0) * 100);

    if (precisionFill) precisionFill.style.width = `${prec}%`;
    if (precisionVal) precisionVal.textContent = `${prec}%`;
    if (recallFill) recallFill.style.width = `${rec}%`;
    if (recallVal) recallVal.textContent = `${rec}%`;

    const starsStr = "★".repeat(data.stars || 0) + "☆".repeat(3 - (data.stars || 0));
    if (starsVal) starsVal.textContent = starsStr;
    if (scoreVal) scoreVal.textContent = `+${data.score || 0} pts`;
  }
}

function logTerminalDiagnostic(msg, type = "info") {
  const diagLog = document.getElementById("diagnosticsLog");
  if (diagLog) {
    const cls = type === "error" ? "error-msg" : type === "success" ? "success-msg" : "dim";
    diagLog.innerHTML = `<span class="${cls}">&gt; ${escapeHtml(msg)}</span>`;
  }
}

function clearTerminalFeedback() {
  const diagLog = document.getElementById("diagnosticsLog");
  const metricsPanel = document.getElementById("diagnosticsMetrics");
  if (diagLog) diagLog.innerHTML = '<span class="dim">&gt; Terminal initialized. Ready to execute forensic warrant search.</span>';
  if (metricsPanel) metricsPanel.style.display = "none";
}

// Live Syntax Validation for the input field
function validatePatternSyntax() {
  const input = document.getElementById("regexInput");
  const indicator = document.getElementById("terminalSyntaxIndicator");
  const statusText = document.getElementById("syntaxStatusText");
  if (!input || !indicator || !statusText) return;

  const val = input.value.trim();
  if (!val) {
    indicator.className = "terminal-badge";
    statusText.textContent = "STANDBY";
    input.classList.remove("invalid-pattern");
    return;
  }

  try {
    new RegExp(val);
    indicator.className = "terminal-badge";
    statusText.textContent = "VALID PATTERN";
    input.classList.remove("invalid-pattern");
  } catch (err) {
    indicator.className = "terminal-badge invalid";
    statusText.textContent = "SYNTAX ERROR";
    input.classList.add("invalid-pattern");
  }
}

// =============================================================================
// 7. SUSPECT ACCUSATION & VERDICT SEQUENCE
// =============================================================================
async function submitAccusation() {
  if (!gameState.selectedSuspect) {
    playSfx("error");
    triggerScreenShake();
    showToast("Select a suspect dossier card from the lineup to accuse.", "warning");
    return;
  }

  const accuseBtn = document.getElementById("accuseBtn");
  if (accuseBtn) accuseBtn.disabled = true;

  try {
    const res = await fetch("/accuse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: gameState.currentCaseId,
        suspect: gameState.selectedSuspect,
      }),
    });

    const data = await res.json();

    // Update reputation & score
    if (typeof data.reputation !== "undefined") {
      gameState.player.reputation = data.reputation;
    }
    if (typeof data.score !== "undefined") {
      gameState.player.score = data.score;
    }
    if (typeof data.coins !== "undefined") {
      gameState.player.coins = data.coins;
    }
    updateHudProfile();

    if (data.solved) {
      // VICTORY SEQUENCE
      playSfx("victory");
      if (!gameState.player.solved_cases.includes(gameState.currentCaseId)) {
        gameState.player.solved_cases.push(gameState.currentCaseId);
      }
      openVictoryModal(data);
    } else {
      // DEFEAT / PENALTY SEQUENCE
      playSfx("defeat");
      triggerScreenShake();
      openDefeatModal(data);
    }
  } catch (err) {
    playSfx("error");
    showToast(`Accusation submission error: ${err}`, "error");
  } finally {
    if (accuseBtn) accuseBtn.disabled = false;
  }
}

function openVictoryModal(data) {
  const modal = document.getElementById("victoryModal");
  if (!modal) return;

  const msgEl = document.getElementById("victoryMessage");
  const subEl = document.getElementById("victorySubtitle");
  const scoreEl = document.getElementById("victoryScoreVal");
  const repEl = document.getElementById("victoryRepVal");
  const coinsEl = document.getElementById("victoryCoinsVal");

  if (msgEl) msgEl.textContent = data.message;
  if (subEl) subEl.textContent = `${gameState.selectedSuspect.toUpperCase()} ARRESTED &amp; CONVICTED`;
  if (scoreEl) scoreEl.textContent = `+${gameState.currentCaseId === 'case_08' ? 500 : 200} pts`;
  if (repEl) repEl.textContent = `+${gameState.currentCaseId === 'case_08' ? 30 : 20} HP`;
  if (coinsEl) coinsEl.textContent = `+${gameState.currentCaseId === 'case_08' ? 50 : 25} 🪙`;

  modal.classList.add("active");
}

function openDefeatModal(data) {
  const modal = document.getElementById("defeatModal");
  if (!modal) return;

  const msgEl = document.getElementById("defeatMessage");
  const repEl = document.getElementById("defeatCurrentRepVal");

  if (msgEl) msgEl.textContent = data.message;
  if (repEl) repEl.textContent = `${data.reputation}%`;

  modal.classList.add("active");
}

function hideVerdictBox() {
  const box = document.getElementById("verdictBox");
  if (box) box.style.display = "none";
}

// =============================================================================
// 8. MATPLOTLIB REPORT VIEWER
// =============================================================================
async function openCaseReportModal(caseId = null) {
  const targetId = caseId || gameState.currentCaseId;
  playSfx("click");

  try {
    const res = await fetch(`/case/${targetId}/report`);
    if (!res.ok) {
      showToast("Report chart could not be generated.", "error");
      return;
    }

    const data = await res.json();
    if (!data.success && !data.report_url) {
      showToast(data.message || "No report available.", "error");
      return;
    }

    const modal = document.getElementById("reportModal");
    const chartImg = document.getElementById("reportChartImg");
    const titleEl = document.getElementById("reportModalTitle");
    const dlLink = document.getElementById("reportDownloadLink");
    const metaGrid = document.getElementById("reportMetaGrid");

    if (titleEl) titleEl.textContent = `Investigation Report: ${data.case_title || targetId}`;
    if (chartImg) chartImg.src = `${data.report_url}?t=${Date.now()}`;
    if (dlLink) dlLink.href = data.report_url;

    if (metaGrid) {
      metaGrid.innerHTML = `
        <div class="reward-pill">
          <span class="reward-label">Stars</span>
          <span class="reward-val" style="color: var(--gold-neon);">★ ${data.stars || 0}/3</span>
        </div>
        <div class="reward-pill">
          <span class="reward-label">Precision</span>
          <span class="reward-val">${Math.round((data.precision || 0) * 100)}%</span>
        </div>
        <div class="reward-pill">
          <span class="reward-label">Recall</span>
          <span class="reward-val">${Math.round((data.recall || 0) * 100)}%</span>
        </div>
        <div class="reward-pill">
          <span class="reward-label">Warrants Used</span>
          <span class="reward-val">${data.searches_used || 0}</span>
        </div>
      `;
    }

    if (modal) modal.classList.add("active");
  } catch (err) {
    showToast(`Error fetching report chart: ${err}`, "error");
  }
}

// =============================================================================
// 9. PICKLE SAVES & CSV LEADERBOARD
// =============================================================================
async function quickSaveSession() {
  playSfx("click");
  try {
    const res = await fetch("/session/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slot: "detective_save" }),
    });
    const data = await res.json();
    if (data.success) {
      showToast("Progress saved to pickle dossier!", "success");
    } else {
      showToast(`Save failed: ${data.message}`, "error");
    }
  } catch (err) {
    showToast(`Save exception: ${err}`, "error");
  }
}

async function quickLoadSession() {
  playSfx("click");
  try {
    const res = await fetch("/session/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slot: "detective_save" }),
    });
    const data = await res.json();
    if (data.success && data.player) {
      gameState.player = data.player;
      updateStartDossier();
      updateHudProfile();
      showToast("Dossier restored from pickle file!", "success");
      loadCase(data.player.current_case_id || "case_01");
    } else {
      showToast(`Load failed: ${data.message || "File not found"}`, "error");
    }
  } catch (err) {
    showToast(`Load exception: ${err}`, "error");
  }
}

async function resetCurrentCaseBudget() {
  playSfx("click");
  try {
    const res = await fetch(`/case/${gameState.currentCaseId}/reset`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast("Case search budget refilled!", "success");
      loadCase(gameState.currentCaseId);
    }
  } catch (err) {
    showToast(`Reset error: ${err}`, "error");
  }
}

async function fetchLeaderboard() {
  try {
    const res = await fetch("/leaderboard");
    if (!res.ok) return;
    const data = await res.json();
    if (data.success) {
      renderLeaderboard(data.leaderboard);
    }
  } catch (err) {
    console.error("Leaderboard fetch error:", err);
  }
}

function renderLeaderboard(entries) {
  const body = document.getElementById("leaderboardModalBody");
  if (!body) return;
  body.innerHTML = "";

  if (!entries || entries.length === 0) {
    body.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">No records registered.</td></tr>';
    return;
  }

  entries.slice(0, 15).forEach((entry, idx) => {
    const tr = document.createElement("tr");
    const stars = "★".repeat(entry.stars || 0);
    const isSolved = (entry.status || "").includes("SOLVED");

    tr.innerHTML = `
      <td style="color: var(--cyan-neon); font-weight: 700;">#${idx + 1}</td>
      <td><strong>${escapeHtml(entry.player_name || "Detective")}</strong></td>
      <td>${escapeHtml(entry.case_title || entry.case_id)}</td>
      <td style="color: var(--gold-neon); font-weight: 700;">${entry.score}</td>
      <td style="color: var(--gold-neon);">${stars || "-"}</td>
      <td><span style="color: ${isSolved ? 'var(--green-neon)' : 'var(--red-neon)'};">${escapeHtml(entry.status)}</span></td>
    `;
    body.appendChild(tr);
  });
}

// =============================================================================
// 10. FIELD NOTES (APPEND-ONLY)
// =============================================================================
async function fetchCaseNotes(caseId) {
  const feed = document.getElementById("notesFeed");
  if (!feed) return;

  try {
    const res = await fetch(`/notes?case_id=${caseId}`);
    if (!res.ok) return;
    const data = await res.json();
    if (data.success) {
      renderCaseNotes(data.notes || []);
    }
  } catch (err) {
    console.error("Failed to load notes:", err);
  }
}

function renderCaseNotes(notes) {
  const feed = document.getElementById("notesFeed");
  if (!feed) return;
  feed.innerHTML = "";

  if (!notes || notes.length === 0) {
    feed.innerHTML = '<span style="color: var(--text-dim); font-size: 11px;">No field notes recorded for this case.</span>';
    return;
  }

  notes.slice().reverse().forEach((n) => {
    const bubble = document.createElement("div");
    bubble.className = "note-bubble";
    bubble.innerHTML = `
      <div class="note-bubble-meta">
        <span>${escapeHtml(n.author || "Detective")}</span>
        <span>${escapeHtml(n.timestamp || "")}</span>
      </div>
      <div class="note-bubble-text">${escapeHtml(n.note)}</div>
    `;
    feed.appendChild(bubble);
  });
}

async function addCaseNote() {
  const input = document.getElementById("noteInput");
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;

  playSfx("click");

  try {
    const res = await fetch("/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: gameState.currentCaseId,
        note: text,
      }),
    });
    const data = await res.json();
    if (data.success) {
      input.value = "";
      renderCaseNotes(data.all_notes || []);
      showToast("Field observation recorded.", "success");
    }
  } catch (err) {
    showToast(`Note error: ${err}`, "error");
  }
}

// =============================================================================
// 11. VISUAL FEEDBACK & TOASTS
// =============================================================================
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `game-toast ${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(40px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 320);
  }, 3200);
}

function triggerScreenShake() {
  document.body.classList.add("screen-shake");
  setTimeout(() => document.body.classList.remove("screen-shake"), 400);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// =============================================================================
// 12. INITIALIZATION & EVENT LISTENERS
// =============================================================================
document.addEventListener("DOMContentLoaded", () => {
  // Audio state restoration
  const savedAudio = localStorage.getItem("regex_audio");
  if (savedAudio !== null) {
    gameState.audioEnabled = savedAudio === "1";
  }
  updateAudioUi();

  // CRT Scanline state
  const crtToggleBtn = document.getElementById("hudCrtToggleBtn");
  if (crtToggleBtn) {
    crtToggleBtn.addEventListener("click", () => {
      gameState.crtEnabled = !gameState.crtEnabled;
      document.body.classList.toggle("crt-enabled", gameState.crtEnabled);
      playSfx("click");
    });
  }

  // Audio Toggles
  const startAudioBtn = document.getElementById("startAudioToggleBtn");
  if (startAudioBtn) startAudioBtn.addEventListener("click", toggleAudio);

  const hudAudioBtn = document.getElementById("hudAudioToggleBtn");
  if (hudAudioBtn) hudAudioBtn.addEventListener("click", toggleAudio);

  // Screen Navigation Buttons
  const startGameBtn = document.getElementById("startGameBtn");
  if (startGameBtn) {
    startGameBtn.addEventListener("click", () => {
      loadCase(gameState.currentCaseId || "case_01");
      switchScreen("game");
    });
  }

  const openMapBtn = document.getElementById("openMapBtn");
  if (openMapBtn) {
    openMapBtn.addEventListener("click", () => switchScreen("map"));
  }

  const mapBackToStartBtn = document.getElementById("mapBackToStartBtn");
  if (mapBackToStartBtn) {
    mapBackToStartBtn.addEventListener("click", () => switchScreen("start"));
  }

  const mapResumeBtn = document.getElementById("mapResumeBtn");
  if (mapResumeBtn) {
    mapResumeBtn.addEventListener("click", () => switchScreen("game"));
  }

  const hudBackToMapBtn = document.getElementById("hudBackToMapBtn");
  if (hudBackToMapBtn) {
    hudBackToMapBtn.addEventListener("click", () => switchScreen("map"));
  }

  // Sandbox Mode Toggle
  const toggleSandboxBtn = document.getElementById("toggleSandboxBtn");
  if (toggleSandboxBtn) {
    toggleSandboxBtn.addEventListener("click", () => {
      gameState.sandboxMode = !gameState.sandboxMode;
      const statusText = document.getElementById("sandboxStatusText");
      if (statusText) {
        statusText.textContent = gameState.sandboxMode ? "Progression: Sandbox (All Open)" : "Progression: Story";
      }
      playSfx("click");
      renderMissionMap();
    });
  }

  // Regex Warrant Input & Helpers
  const searchBtn = document.getElementById("searchBtn");
  const regexInput = document.getElementById("regexInput");

  if (searchBtn) searchBtn.addEventListener("click", executeWarrant);
  if (regexInput) {
    regexInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") executeWarrant();
    });
    regexInput.addEventListener("input", validatePatternSyntax);
  }

  document.querySelectorAll(".token-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const token = btn.dataset.token;
      if (regexInput && token) {
        regexInput.value += token;
        validatePatternSyntax();
        regexInput.focus();
        playSfx("click");
      }
    });
  });

  // Evidence Actions
  const clearHighlightsBtn = document.getElementById("clearHighlightsBtn");
  if (clearHighlightsBtn) {
    clearHighlightsBtn.addEventListener("click", () => {
      highlightMatches([]);
      playSfx("click");
    });
  }

  const copyEvidenceBtn = document.getElementById("copyEvidenceBtn");
  if (copyEvidenceBtn) {
    copyEvidenceBtn.addEventListener("click", () => {
      if (gameState.activeCaseData && gameState.activeCaseData.evidence_text) {
        navigator.clipboard.writeText(gameState.activeCaseData.evidence_text).then(() => {
          showToast("Evidence stream copied to clipboard!", "success");
          playSfx("click");
        });
      }
    });
  }

  // Accusation Button
  const accuseBtn = document.getElementById("accuseBtn");
  if (accuseBtn) accuseBtn.addEventListener("click", submitAccusation);

  // Field Notes
  const addNoteBtn = document.getElementById("addNoteBtn");
  const noteInput = document.getElementById("noteInput");
  if (addNoteBtn) addNoteBtn.addEventListener("click", addCaseNote);
  if (noteInput) {
    noteInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") addCaseNote();
    });
  }

  // Save / Load / Reset
  const hudSaveBtn = document.getElementById("hudSaveBtn");
  if (hudSaveBtn) hudSaveBtn.addEventListener("click", quickSaveSession);

  const hudLoadBtn = document.getElementById("hudLoadBtn");
  if (hudLoadBtn) hudLoadBtn.addEventListener("click", quickLoadSession);

  const startLoadBtn = document.getElementById("startLoadBtn");
  if (startLoadBtn) startLoadBtn.addEventListener("click", quickLoadSession);

  const hudResetBtn = document.getElementById("hudResetBtn");
  if (hudResetBtn) hudResetBtn.addEventListener("click", resetCurrentCaseBudget);

  // Modals Interactions
  const victoryReportBtn = document.getElementById("victoryReportBtn");
  if (victoryReportBtn) {
    victoryReportBtn.addEventListener("click", () => {
      document.getElementById("victoryModal").classList.remove("active");
      openCaseReportModal(gameState.currentCaseId);
    });
  }

  const victoryMapBtn = document.getElementById("victoryMapBtn");
  if (victoryMapBtn) {
    victoryMapBtn.addEventListener("click", () => {
      document.getElementById("victoryModal").classList.remove("active");
      switchScreen("map");
    });
  }

  const victoryNextBtn = document.getElementById("victoryNextBtn");
  if (victoryNextBtn) {
    victoryNextBtn.addEventListener("click", () => {
      document.getElementById("victoryModal").classList.remove("active");
      const currentIdx = gameState.allCases.findIndex((c) => c.case_id === gameState.currentCaseId);
      if (currentIdx !== -1 && currentIdx + 1 < gameState.allCases.length) {
        loadCase(gameState.allCases[currentIdx + 1].case_id);
      } else {
        switchScreen("map");
      }
    });
  }

  const defeatRetryBtn = document.getElementById("defeatRetryBtn");
  if (defeatRetryBtn) {
    defeatRetryBtn.addEventListener("click", () => {
      document.getElementById("defeatModal").classList.remove("active");
      resetCurrentCaseBudget();
    });
  }

  const defeatMapBtn = document.getElementById("defeatMapBtn");
  if (defeatMapBtn) {
    defeatMapBtn.addEventListener("click", () => {
      document.getElementById("defeatModal").classList.remove("active");
      switchScreen("map");
    });
  }

  // Report Modal Dismiss
  const closeReportBtn = document.getElementById("closeReportBtn");
  const closeReportFooterBtn = document.getElementById("closeReportFooterBtn");
  [closeReportBtn, closeReportFooterBtn].forEach((btn) => {
    if (btn) {
      btn.addEventListener("click", () => {
        document.getElementById("reportModal").classList.remove("active");
        playSfx("click");
      });
    }
  });

  // Leaderboard Modal
  const openLeaderboardBtn = document.getElementById("openLeaderboardBtn");
  const closeLeaderboardBtn = document.getElementById("closeLeaderboardBtn");
  const closeLeaderboardFooterBtn = document.getElementById("closeLeaderboardFooterBtn");
  const refreshLeaderboardModalBtn = document.getElementById("refreshLeaderboardModalBtn");

  if (openLeaderboardBtn) {
    openLeaderboardBtn.addEventListener("click", () => {
      fetchLeaderboard();
      document.getElementById("leaderboardModal").classList.add("active");
      playSfx("click");
    });
  }

  [closeLeaderboardBtn, closeLeaderboardFooterBtn].forEach((btn) => {
    if (btn) {
      btn.addEventListener("click", () => {
        document.getElementById("leaderboardModal").classList.remove("active");
        playSfx("click");
      });
    }
  });

  if (refreshLeaderboardModalBtn) {
    refreshLeaderboardModalBtn.addEventListener("click", () => {
      fetchLeaderboard();
      playSfx("click");
    });
  }

  // Initial Boot Sequence
  syncPlayerProfile();
  fetchAllCases();
});
