/**
 * Regex Detective - Client-side Game Controller
 */

let currentCaseId = "case_01";
let activeCaseData = null;

// DOM Elements
const elements = {
  caseTitle: document.getElementById("caseTitle"),
  caseDiff: document.getElementById("caseDiff"),
  caseBriefing: document.getElementById("caseBriefing"),
  evidenceBox: document.getElementById("evidenceBox"),
  warrantDots: document.getElementById("warrantDots"),
  warrantText: document.getElementById("warrantText"),
  regexInput: document.getElementById("regexInput"),
  searchBtn: document.getElementById("searchBtn"),
  feedbackBox: document.getElementById("feedbackBox"),
  feedbackText: document.getElementById("feedbackText"),
  feedbackMeta: document.getElementById("feedbackMeta"),
  cluesGrid: document.getElementById("cluesGrid"),
  suspectsList: document.getElementById("suspectsList"),
  accuseBtn: document.getElementById("accuseBtn"),
  accusationStatus: document.getElementById("accusationStatus"),
  playerReputation: document.getElementById("playerReputation"),
  playerScore: document.getElementById("playerScore"),
  caseScore: document.getElementById("caseScore"),
  resetBtn: document.getElementById("resetBtn"),
};

// Escape HTML characters safely
function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Fetch case details from server
async function loadCase(caseId) {
  currentCaseId = caseId;
  clearFeedback();
  clearAccusationStatus();

  // Highlight active tab
  document.querySelectorAll(".case-tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.caseId === caseId);
  });

  try {
    const res = await fetch(`/case/${caseId}`);
    const data = await res.json();

    if (!data.success) {
      showFeedback(`Failed to load case: ${data.message}`, "error");
      return;
    }

    activeCaseData = data;
    renderCaseDetails(data);
  } catch (err) {
    showFeedback(`Network error while loading case: ${err}`, "error");
  }
}

// Render case metadata and UI elements
function renderCaseDetails(data) {
  elements.caseTitle.textContent = data.title;
  elements.caseDiff.textContent = data.difficulty;
  elements.caseBriefing.textContent = data.briefing;
  elements.evidenceBox.textContent = data.evidence_text || "No evidence text found.";

  updateWarrantBudget(data.remaining_budget, data.search_budget);
  renderCollectedClues(data.collected_clues);
  renderSuspects(data.suspects);

  if (elements.caseScore) {
    elements.caseScore.textContent = `${data.case_score || 0} pts`;
  }
  if (elements.playerReputation) {
    elements.playerReputation.textContent = `${data.player_reputation ?? 100}%`;
  }
}

// Update warrant dots
function updateWarrantBudget(remaining, total) {
  elements.warrantDots.innerHTML = "";
  const max = Math.max(total, remaining);
  for (let i = 0; i < max; i++) {
    const dot = document.createElement("div");
    dot.className = `warrant-dot ${i >= remaining ? "spent" : ""}`;
    elements.warrantDots.appendChild(dot);
  }
  elements.warrantText.textContent = `${remaining} / ${total} warrants left`;

  elements.searchBtn.disabled = remaining <= 0;
  if (remaining <= 0) {
    elements.searchBtn.title = "Search budget exhausted!";
  } else {
    elements.searchBtn.title = "Execute warrant search";
  }
}

// Render collected clues list
function renderCollectedClues(clues) {
  elements.cluesGrid.innerHTML = "";
  if (!clues || clues.length === 0) {
    elements.cluesGrid.innerHTML =
      '<span class="clue-tag empty-state">No clues confirmed yet. Issue a warrant above!</span>';
    return;
  }

  clues.forEach((clue) => {
    const tag = document.createElement("span");
    tag.className = "clue-tag";
    tag.innerHTML = `<span>🔍</span> ${escapeHtml(clue)}`;
    elements.cluesGrid.appendChild(tag);
  });
}

// Render suspects for accusation
function renderSuspects(suspects) {
  elements.suspectsList.innerHTML = "";
  if (!suspects || suspects.length === 0) {
    elements.suspectsList.innerHTML = "<p>No suspects recorded.</p>";
    return;
  }

  suspects.forEach((name, idx) => {
    const option = document.createElement("div");
    option.className = "suspect-option";
    const radioId = `suspect_${idx}`;
    option.innerHTML = `
      <input type="radio" id="${radioId}" name="suspectRadio" value="${escapeHtml(name)}">
      <label class="suspect-label" for="${radioId}">
        <span class="suspect-icon">🕵️</span>
        <span>${escapeHtml(name)}</span>
      </label>
    `;
    elements.suspectsList.appendChild(option);
  });
}

// Highlight matched regex in evidence box
function highlightEvidence(matches) {
  if (!activeCaseData || !activeCaseData.evidence_text) return;
  let rawText = activeCaseData.evidence_text;

  if (!matches || matches.length === 0) {
    elements.evidenceBox.textContent = rawText;
    return;
  }

  // Escape base text first
  let escaped = escapeHtml(rawText);

  // Sort unique matches by length descending so longer substrings match first
  const uniqueMatches = Array.from(new Set(matches)).sort((a, b) => b.length - a.length);

  uniqueMatches.forEach((m) => {
    if (!m) return;
    const escapedMatch = escapeHtml(m);
    // Replace all occurrences using regex safe escaping
    const safeRegex = new RegExp(escapedMatch.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&"), "g");
    escaped = escaped.replace(safeRegex, `<mark class="match-highlight">${escapedMatch}</mark>`);
  });

  elements.evidenceBox.innerHTML = escaped;
}

// Submit regex warrant search
async function executeSearch() {
  const pattern = elements.regexInput.value.trim();
  if (!pattern) {
    showFeedback("Please enter a regex search pattern.", "error");
    return;
  }

  clearFeedback();
  elements.searchBtn.disabled = true;
  elements.searchBtn.innerHTML = "<span>Searching...</span>";

  try {
    const res = await fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: currentCaseId,
        pattern: pattern,
      }),
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      showFeedback(data.message || "Warrant execution failed.", "error");
      if (typeof data.remaining_budget !== "undefined") {
        updateWarrantBudget(data.remaining_budget, activeCaseData.search_budget);
      }
      return;
    }

    // Update case display with search results
    updateWarrantBudget(data.remaining_budget, activeCaseData.search_budget);
    renderCollectedClues(data.collected_clues);
    highlightEvidence(data.matches);

    // Update global player score
    if (elements.playerScore) {
      elements.playerScore.textContent = `${data.total_score} pts`;
    }
    if (elements.caseScore) {
      elements.caseScore.textContent = `${data.score} pts`;
    }

    // Format stars and score meta
    const starString = "★".repeat(data.stars) + "☆".repeat(3 - data.stars);
    const metaHtml = `
      <span>Stars: ${starString}</span>
      <span>Precision: ${(data.precision * 100).toFixed(0)}%</span>
      <span>Recall: ${(data.recall * 100).toFixed(0)}%</span>
      <span>Points: +${data.score}</span>
    `;

    // Choose feedback theme
    let statusType = "success";
    if (data.false_matches && data.false_matches.length > 0) {
      statusType = "warning";
    }
    if (data.matches.length === 0) {
      statusType = "error";
    }

    showFeedback(data.feedback, statusType, metaHtml);
  } catch (err) {
    showFeedback(`Search failed due to unexpected error: ${err}`, "error");
  } finally {
    elements.searchBtn.disabled =
      activeCaseData && activeCaseData.remaining_budget <= 0;
    elements.searchBtn.innerHTML = "<span>Issue Warrant 🔍</span>";
  }
}

// Submit suspect accusation
async function submitAccusation() {
  const selected = document.querySelector('input[name="suspectRadio"]:checked');
  if (!selected) {
    showAccusationStatus("Please select a suspect from the list to accuse.", false);
    return;
  }

  const suspectName = selected.value;
  elements.accuseBtn.disabled = true;

  try {
    const res = await fetch("/accuse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: currentCaseId,
        suspect: suspectName,
      }),
    });

    const data = await res.json();

    if (elements.playerReputation) {
      elements.playerReputation.textContent = `${data.reputation}%`;
    }
    if (elements.playerScore && data.score) {
      elements.playerScore.textContent = `${data.score} pts`;
    }

    showAccusationStatus(data.message, data.solved);
  } catch (err) {
    showAccusationStatus(`Failed submitting accusation: ${err}`, false);
  } finally {
    elements.accuseBtn.disabled = false;
  }
}

// Reset current case
async function resetCurrentCase() {
  try {
    const res = await fetch(`/case/${currentCaseId}/reset`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      loadCase(currentCaseId);
      showFeedback("Case warrants and search budget have been reset.", "success");
    }
  } catch (err) {
    showFeedback(`Failed to reset case: ${err}`, "error");
  }
}

// UI Feedback helpers
function showFeedback(text, type = "success", meta = "") {
  elements.feedbackBox.className = `feedback-box active ${type}`;
  elements.feedbackText.textContent = text;
  elements.feedbackMeta.innerHTML = meta;
}

function clearFeedback() {
  elements.feedbackBox.className = "feedback-box";
  elements.feedbackText.textContent = "";
  elements.feedbackMeta.innerHTML = "";
}

function showAccusationStatus(message, isSuccess) {
  elements.accusationStatus.className = `accusation-status-box active ${
    isSuccess ? "feedback-box success" : "feedback-box error"
  }`;
  elements.accusationStatus.textContent = message;
}

function clearAccusationStatus() {
  elements.accusationStatus.className = "accusation-status-box";
  elements.accusationStatus.textContent = "";
}

// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  // Case tab navigation clicks
  document.querySelectorAll(".case-tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      loadCase(btn.dataset.caseId);
    });
  });

  // Regex helper chips
  document.querySelectorAll(".helper-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const token = chip.dataset.token || chip.textContent;
      elements.regexInput.value += token;
      elements.regexInput.focus();
    });
  });

  // Search button and Enter key
  elements.searchBtn.addEventListener("click", executeSearch);
  elements.regexInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      executeSearch();
    }
  });

  // Accusation button
  elements.accuseBtn.addEventListener("click", submitAccusation);

  // Reset button
  if (elements.resetBtn) {
    elements.resetBtn.addEventListener("click", resetCurrentCase);
  }

  // Initial load
  loadCase("case_01");
});
