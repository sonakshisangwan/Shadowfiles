# Regex Detective / Shadowfiles 🕵️✨

> **A full-stack cybercrime investigation game where code meets forensic pattern extraction.**  
> Built with **Flask**, **Python `re`**, **OOP**, **Pandas**, **NumPy**, **Matplotlib**, and a cozy **pink & white** terminal interface.

---

## 📖 1. Project Overview & Theme

In **Regex Detective / Shadowfiles**, the player acts as a rookie cybercrime investigator assigned to the Delhi Cyber Bureau. An underground cybercrime network—the **Apex Syndicate**—is laundering funds, compromising ATMs, intercepting phone lines, and disguising classified memos across Indian metropolitan hubs (Connaught Place, Karol Bagh, Cyber Hub).

Each case presents **messy digital evidence** such as server wiretaps, phone records, CCTV heat matrices, payment gateways, and encrypted ciphers. The player writes **regular expressions** to extract authentic clues, filter out deceptive decoys, manage limited warrant budgets, and apprehend the mastermind.

### Visual Aesthetic
The UI breaks away from generic dark cyberpunk templates, employing a **soft, cozy, handmade aesthetic** with:
- Warm blush pink (`#d85d7f`) and cream white (`#ffffff`) palette
- Delicate rounded cards and soft drop shadows
- Animated live match highlighting directly inside log dossiers
- Intuitive regex helper tokens (`\d`, `\w`, `+`, `*`, `{3}`, `@`, `\.`, `^`, `$`)

---

## 🛠️ 2. Technology Stack

- **Backend Framework**: [Flask](https://flask.palletsprojects.com/) (REST API architecture)
- **Regex & Pattern Engine**: Python standard `re` module (`re.compile`, `re.findall`, `re.sub`, error trapping `re.error`)
- **Object-Oriented Programming (OOP)**:
  - `Evidence` hierarchy (`Evidence`, `EmailEvidence`, `ChatEvidence`)
  - `Case` domain model with encapsulated answers and decoy verification
  - `Player` profile tracking score, reputation, and inventory
  - `DetectiveEngine` for warrant execution and scoring
- **Memory Efficiency**: Python **Generators** (`yield`) for line-by-line streaming of large log files
- **Data Science & Forensics**:
  - **Pandas**: Structured banking telemetry table analysis (`forensics_logs.csv`)
  - **NumPy**: $8 \times 8$ matrix grid representing CCTV thermal sensors
  - **Matplotlib**: Automatic headless generation of visual post-case report charts
- **Persistence Layer**:
  - **JSON**: Case definitions and serialized progression (`data/cases/`)
  - **Pickle**: Binary session state saving and restoration (`data/saves/`)
  - **CSV**: Persistent player leaderboard (`data/leaderboard.csv`)
  - **Append-Only Text**: Timestamped detective field journal (`data/notes/`)
- **Frontend**: HTML5, Vanilla CSS3, Modern ES6 JavaScript (`fetch` API, live DOM highlighting)

---

## 🕹️ 3. Core Gameplay & Scoring Mechanics

### Mathematical Scoring Logic
$$\text{Score} = (\text{Recall} \times 500) + (\text{Precision} \times 300) + \text{Brevity Bonus} - \text{Decoy Penalty} - \text{Attempt Penalty}$$

1. **Precision**: $\frac{\text{Correct Clues Found}}{\text{Total Matches Caught}}$ (Penalizes false positives and decoys)
2. **Recall**: $\frac{\text{Correct Clues Found}}{\text{Total Target Clues In Case}}$ (Measures completeness)
3. **Brevity Bonus**: Up to $+50$ points for concise, elegant regex when all clues are identified cleanly without noise.
4. **Decoy Penalty**: $-40$ points for each decoy triggered by an overly broad pattern.
5. **Search Budget**: Each search consumes $1$ warrant. If exhausted, searches are blocked (`WarrantBudgetExceeded`).
6. **Reputation & Accusation**:
   - Correct Accusation: $+20$ Reputation, $+200$ points ($+500$ on final boss), marks case **SOLVED**.
   - False Accusation: $-20$ Reputation. If reputation drops to $0\%$, the case is marked **FAILED**.
7. **Star Rating**:
   - `★★★` (3 Stars): $100\%$ Recall + $100\%$ Precision (Zero decoys triggered)
   - `★★☆` (2 Stars): $100\%$ Recall with decoys, or $\ge 50\%$ balanced
   - `★☆☆` (1 Star): Partial clues captured
   - `☆☆☆` (0 Stars): Dead end (no valid clues)

---

## 🗂️ 4. Progression of the 8 Playable Cases

| Case | Title | Regex / Tool Focus | Target Evidence | Culprit |
|---|---|---|---|---|
| **Case 01** | **Operation Dark Rupee** | `\d`, character sets, length | Delhi 6-digit PIN codes (`110XXX`) | `Rajesh Oberoi` |
| **Case 02** | **Operation Hawala Wire** | Quantifiers & anchors | Active phone lines (`+91-98XXX-XXXXX`) | `Vikram Malhotra` |
| **Case 03** | **The UPI Syndicate** | Groups `()` & alternation `\|` | Bank UPI handles (`@okhdfcbank\|@oksbi`) | `Pooja Verma` |
| **Case 04** | **The Midnight Alibi** | Dates & 24-hr times | Late-night timestamps (`2026-11-0[45] (?:23\|00\|01):\d{2}`) | `Alok Verma` |
| **Case 05** | **Forensics Lab: Data Breach** | **Pandas** DataFrame | Rogue device telemetry (`DEV-[A-Z]{3}-\d{4}`) | `Karan Saxena` |
| **Case 06** | **CCTV Surveillance Grid** | **NumPy** $8 \times 8$ Matrix | Thermal camera surge coordinates (`CAM-[A-H][1-8]`) | `Suresh Nair` |
| **Case 07** | **Operation Redacted Shadow** | **`re.sub()`** De-masking | Unmasked secret project codes (`CODE-[A-Z]{4,5}-\d{2}`) | `Monica Dsouza` |
| **Case 08** | **👑 Final Boss: Vedic Vault** | **Master Mixed Challenge** | Zero-hour time + Architect line + Treasury UPI + Vedic key | `Dr. Aryan Dev` |

---

## 📁 5. Project Directory Structure

```text
regex_detective/
├── app.py                     # Flask application & REST API routes
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation & presentation guide
├── .gitignore                 # Version control filter
├── game/                      # Core OOP domain package
│   ├── __init__.py            # Package exports
│   ├── evidence.py            # Evidence hierarchy, Case model & generators
│   ├── engine.py              # Regex matching, scoring math & SearchResult
│   ├── exceptions.py          # Custom game exceptions hierarchy
│   ├── storage.py             # Pickle session, CSV leaderboard & notes
│   ├── analytics.py           # Pandas telemetry, NumPy CCTV & Matplotlib reports
│   └── vault.py               # Final Boss Vedic Vault case & chamber logic
├── data/                      # File-based persistence directory
│   ├── cases/                 # Case definitions (case_01.json -> case_08.json)
│   ├── evidence/              # Raw data files (forensics_logs.csv, intercepts)
│   ├── saves/                 # Binary pickle player saves (*.pkl)
│   ├── notes/                 # Append-only detective notes (detective_notes.txt)
│   ├── reports/               # Generated Matplotlib charts (*_report.png)
│   └── leaderboard.csv        # Persistent CSV leaderboard
├── static/                    # Frontend assets
│   ├── css/
│   │   └── style.css          # Cozy soft pink/white theme stylesheet
│   └── js/
│       └── app.js             # Async Fetch controller & live match highlighter
└── templates/
    └── index.html             # Main detective dashboard interface
```

---

## 🚀 6. Local Setup & Quickstart

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- `pip` package manager

### Installation Steps

1. **Navigate to the project directory**:
   ```powershell
   cd "regex_detective"
   ```

2. **(Optional) Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start the Flask server**:
   ```powershell
   python app.py
   ```

5. **Open your web browser**:
   Navigate to:
   ```text
   http://127.0.0.1:5000/
   ```
   *(Or `/play` to jump directly into the investigation dashboard)*

---

## 📡 7. REST API Reference

| Endpoint | Method | Payload / Params | Description |
|---|---|---|---|
| `/` | `GET` | Header: `Accept: text/html` or `application/json` | Serves dashboard UI or API system health JSON |
| `/case/<id>` | `GET` | URL param (e.g. `1`, `case_01`, `vault`) | Returns case briefing, evidence text, suspects & budget |
| `/search` | `POST` | `{"case_id": "case_01", "pattern": "..."}` | Validates regex, updates budget, scores warrant |
| `/accuse` | `POST` | `{"case_id": "case_01", "suspect": "..."}` | Accuses suspect, updates reputation, generates report |
| `/case/<id>/reset` | `POST` | URL param | Restores search budget for re-attempts |
| `/case/<id>/report`| `GET` | URL param | Returns case summary metrics and Matplotlib chart path |
| `/reports/<file>`  | `GET` | Filename (e.g. `case_01_report.png`) | Serves generated visual report image binary |
| `/session/save`    | `POST` | `{"slot": "save_01"}` | Saves player state using Python `pickle` |
| `/session/load`    | `POST` | `{"slot": "save_01"}` | Deserializes player state from pickle file |
| `/session/saves`   | `GET` | None | Lists available local save slots |
| `/leaderboard`     | `GET` | None | Returns top scores from `data/leaderboard.csv` |
| `/notes`           | `GET` / `POST` | `{"case_id": "...", "note": "..."}` | Appends or retrieves timestamped detective field notes |

---

## 🎓 8. Viva & Presentation Guide

Use this section as a reference when presenting the project in class, vivas, or technical demonstrations.

### 🎤 30-Second Elevator Pitch
> *"Regex Detective is a gamified cybercrime forensic dashboard. Instead of dry theoretical regex exercises, students step into the shoes of a cyber detective solving 8 narrative cases. Using Flask, Python's `re` engine, Pandas, NumPy, and Matplotlib, players analyze intercepted chats, bank telemetry, and thermal grids. Overly broad patterns catch realistic decoys and penalize precision, while elegant patterns unlock stars, generate visual case analytics charts, and breach the final multi-chamber Vedic Vault."*

### 🔑 Key Architectural Design Decisions
1. **Why Python's `re` instead of client-side JavaScript regex?**
   - *Security & Engine Integrity*: Server-side validation guarantees consistent POSIX/Python regex behavior, prevents client manipulation of game state, and allows catching `re.error` to return custom in-game exceptions (`InvalidWarrantError`).
2. **How does the scoring math prevent brute-force guessing?**
   - *Set Math*: Player matches and target answers are modeled as Python `set`s.
   - Precision ($\text{Hits} / \text{Total Matches}$) immediately drops if a player writes a lazy catch-all like `.*` or `\d+`, which triggers decoy traps.
   - Attempt penalties and hard warrant limits prevent repetitive trial-and-error.
3. **How are generators used?**
   - `Evidence.lines()` is a Python generator (`yield`). For large logs (like multi-megabyte server dumps), evidence is streamed line-by-line without consuming excessive RAM.
4. **Why multiple persistence methods (JSON, Pickle, CSV, Text)?**
   - To demonstrate appropriate file handling for different data models:
     - **JSON** for human-readable, schema-based case configuration.
     - **Pickle** for binary object serialization of the active `Player` session state.
     - **CSV** for tabular, sortable leaderboard history.
     - **Append-Only Text** for timestamped audit logs and field notes.
5. **How does Matplotlib integrate into a web app safely?**
   - Matplotlib defaults to GUI backends (like Tkinter/Qt), which crash headless web servers. By explicitly invoking `matplotlib.use("Agg")`, charts are rendered directly into headless image buffers and closed with `plt.close(fig)` to eliminate memory leaks.

### ❓ Sample Viva Questions & Quick Answers

- **Q: What happens if a player types an invalid regular expression like `[0-9(`?**  
  *A:* The engine intercepts the syntax error through a `try...except re.error` block and raises our custom domain exception `InvalidWarrantError`. Instead of an HTTP 500 crash, the API returns HTTP 400 with the friendly message *"Invalid warrant! Regex error: unterminated character set"*.

- **Q: How does Case 7 use `re.sub()`?**  
  *A:* Case 7 contains redacted darknet memos where sensitive project codes are obscured by noise wrappers (`###CODE-...###`). The player uses substitution patterns to strip the noise or extract the unmasked authorization tokens.

- **Q: What makes the Vedic Vault finale unique?**  
  *A:* Unlike earlier cases that test one isolated pattern type, the Vedic Vault combines zero-hour timestamps, phone lines, UPI handles, and redacted master keys across 4 distinct security chambers. The backend tracks breach percentage and awards special `MASTER_SOLVED` status upon indicting the Architect.

---

## 📜 9. License & Academic Attribution
Developed as an advanced Computer Programming academic mini project. Free to extend for educational and learning purposes.
