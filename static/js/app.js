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
  saveBtn: document.getElementById("saveBtn"),
  loadBtn: document.getElementById("loadBtn"),
  noteInput: document.getElementById("noteInput"),
  addNoteBtn: document.getElementById("addNoteBtn"),
  notesList: document.getElementById("notesList"),
  leaderboardBody: document.getElementById("leaderboardBody"),
  refreshLeaderboardBtn: document.getElementById("refreshLeaderboardBtn"),
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
    fetchNotes(caseId);
  } catch (err) {
    showFeedback(`Network error while loading case: ${err}`, "error");
  }
}

// Render case metadata and UI elements
function renderCaseDetails(data) {
  elements.caseTitle.textContent = data.title;
  elements.caseDiff.textContent = data.difficulty;
  if (data.vault_status) {
    const v = data.vault_status;
    const chambersList = Object.entries(v.chambers)
      .map(([name, ok]) => `  ${ok ? "🔓 [UNLOCKED]" : "🔒 [SEALED]"} ${name}`)
      .join("\n");
    elements.caseBriefing.textContent = `${data.briefing}\n\n👑 VEDIC VAULT CHAMBER SEALS: ${v.layers_unlocked}/${v.total_layers} Breached (${v.percentage}%)\n${chambersList}`;
  } else {
    elements.caseBriefing.textContent = data.briefing;
  }
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

  let escaped = escapeHtml(rawText);
  const uniqueMatches = Array.from(new Set(matches)).sort((a, b) => b.length - a.length);

  uniqueMatches.forEach((m) => {
    if (!m) return;
    const escapedMatch = escapeHtml(m);
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

    updateWarrantBudget(data.remaining_budget, activeCaseData.search_budget);
    renderCollectedClues(data.collected_clues);
    highlightEvidence(data.matches);

    if (elements.playerScore) {
      elements.playerScore.textContent = `${data.total_score} pts`;
    }
    if (elements.caseScore) {
      elements.caseScore.textContent = `${data.score} pts`;
    }

    const starString = "★".repeat(data.stars) + "☆".repeat(3 - data.stars);
    const metaHtml = `
      <span>Stars: ${starString}</span>
      <span>Precision: ${(data.precision * 100).toFixed(0)}%</span>
      <span>Recall: ${(data.recall * 100).toFixed(0)}%</span>
      <span>Points: +${data.score}</span>
    `;

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

    showAccusationStatus(data.message, data.solved, data.report_url);
    fetchLeaderboard();
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

// Pickle Session Save / Load
async function saveGameSession() {
  try {
    const res = await fetch("/session/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slot: "detective_save" }),
    });
    const data = await res.json();
    if (data.success) {
      showFeedback(`Progress saved via pickle: ${data.message}`, "success");
    } else {
      showFeedback(`Save failed: ${data.message}`, "error");
    }
  } catch (err) {
    showFeedback(`Error saving session: ${err}`, "error");
  }
}

async function loadGameSession() {
  try {
    const res = await fetch("/session/load", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slot: "detective_save" }),
    });
    const data = await res.json();
    if (data.success) {
      showFeedback("Player session restored from pickle save file!", "success");
      if (elements.playerReputation) {
        elements.playerReputation.textContent = `${data.player.reputation}%`;
      }
      if (elements.playerScore) {
        elements.playerScore.textContent = `${data.player.score} pts`;
      }
      loadCase(data.player.current_case_id || "case_01");
    } else {
      showFeedback(`Load failed: ${data.message}`, "error");
    }
  } catch (err) {
    showFeedback(`Error loading session: ${err}`, "error");
  }
}

// Field Notes
async function addDetectiveNote() {
  if (!elements.noteInput) return;
  const note = elements.noteInput.value.trim();
  if (!note) return;

  try {
    const res = await fetch("/notes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        case_id: currentCaseId,
        note: note,
      }),
    });
    const data = await res.json();
    if (data.success) {
      elements.noteInput.value = "";
      renderNotes(data.all_notes);
    }
  } catch (err) {
    console.error("Failed to append note:", err);
  }
}

async function fetchNotes(caseId) {
  if (!elements.notesList) return;
  try {
    const res = await fetch(`/notes?case_id=${caseId}`);
    const data = await res.json();
    if (data.success) {
      renderNotes(data.notes);
    }
  } catch (err) {
    console.error("Failed to fetch notes:", err);
  }
}

function renderNotes(notes) {
  if (!elements.notesList) return;
  elements.notesList.innerHTML = "";
  if (!notes || notes.length === 0) {
    elements.notesList.innerHTML =
      '<div style="color: var(--text-light); font-size: 12px; font-style: italic;">No field notes recorded for this case yet.</div>';
    return;
  }

  notes.slice().reverse().forEach((n) => {
    const item = document.createElement("div");
    item.className = "note-item";
    item.innerHTML = `
      <div class="note-header">
        <span>${escapeHtml(n.author || "Detective")}</span>
        <span>${escapeHtml(n.timestamp || "")}</span>
      </div>
      <div class="note-text">${escapeHtml(n.note)}</div>
    `;
    elements.notesList.appendChild(item);
  });
}

// Leaderboard
async function fetchLeaderboard() {
  if (!elements.leaderboardBody) return;
  try {
    const res = await fetch("/leaderboard");
    const data = await res.json();
    if (data.success) {
      renderLeaderboard(data.leaderboard);
    }
  } catch (err) {
    console.error("Failed to load leaderboard:", err);
  }
}

function renderLeaderboard(entries) {
  if (!elements.leaderboardBody) return;
  elements.leaderboardBody.innerHTML = "";
  if (!entries || entries.length === 0) {
    elements.leaderboardBody.innerHTML =
      '<tr><td colspan="5" style="text-align: center; color: var(--text-light); padding: 12px;">No leaderboard entries recorded yet.</td></tr>';
    return;
  }

  entries.slice(0, 10).forEach((row) => {
    const tr = document.createElement("tr");
    const stars = "★".repeat(row.stars || 0);
    const statusClass = row.status === "SOLVED" ? "solved" : "failed";

    tr.innerHTML = `
      <td><strong>${escapeHtml(row.player_name)}</strong></td>
      <td>${escapeHtml(row.case_title || row.case_id)}</td>
      <td style="color: var(--primary-pink); font-weight: 700;">${row.score}</td>
      <td style="color: #e09214;">${stars || "-"}</td>
      <td><span class="badge-status ${statusClass}">${escapeHtml(row.status)}</span></td>
    `;
    elements.leaderboardBody.appendChild(tr);
  });
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

function showAccusationStatus(message, isSuccess, reportUrl = null) {
  elements.accusationStatus.className = `accusation-status-box active ${
    isSuccess ? "feedback-box success" : "feedback-box error"
  }`;
  let html = `<div>${escapeHtml(message)}</div>`;
  if (reportUrl) {
    html += `
      <div style="margin-top: 10px;">
        <a href="${reportUrl}" target="_blank" class="btn-secondary" style="display: inline-flex; align-items: center; gap: 6px; text-decoration: none; padding: 6px 12px; font-weight: 700;">
          <span>📊 View Matplotlib Case Report Chart</span>
        </a>
      </div>
    `;
  }
  elements.accusationStatus.innerHTML = html;
}

function clearAccusationStatus() {
  elements.accusationStatus.className = "accusation-status-box";
  elements.accusationStatus.innerHTML = "";
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

  // Save / Load buttons
  if (elements.saveBtn) {
    elements.saveBtn.addEventListener("click", saveGameSession);
  }
  if (elements.loadBtn) {
    elements.loadBtn.addEventListener("click", loadGameSession);
  }

  // Notes
  if (elements.addNoteBtn) {
    elements.addNoteBtn.addEventListener("click", addDetectiveNote);
  }
  if (elements.noteInput) {
    elements.noteInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") addDetectiveNote();
    });
  }

  // Leaderboard
  if (elements.refreshLeaderboardBtn) {
    elements.refreshLeaderboardBtn.addEventListener("click", fetchLeaderboard);
  }

  // Initial load
  loadCase("case_01");
  fetchLeaderboard();
});
