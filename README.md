# Regex Detective / Shadowfiles

A full-stack cybercrime investigation game where code meets forensic pattern extraction.  
Built with Flask, Python `re`, OOP, Pandas, NumPy, Matplotlib, and a cozy pink-and-white interface.

## 1. Project Overview

In **Regex Detective / Shadowfiles**, the player acts as a rookie cybercrime investigator assigned to the Delhi Cyber Bureau. An underground cybercrime network, the **Apex Syndicate**, is laundering funds, compromising ATMs, intercepting phone lines, and disguising classified memos across Indian metropolitan hubs like Connaught Place, Karol Bagh, and Cyber Hub.

Each case presents messy digital evidence such as server wiretaps, phone records, CCTV heat matrices, payment gateways, and encrypted ciphers. The player writes regular expressions to extract authentic clues, filter out deceptive decoys, manage limited warrant budgets, and apprehend the mastermind.

## Visual Aesthetic

The UI avoids generic cyberpunk templates and uses a soft, cozy, handmade aesthetic with:
- Warm blush pink and cream white palette
- Rounded cards and soft shadows
- Live match highlighting inside log dossiers
- Regex helper tokens such as `\d`, `\w`, `+`, `*`, `{3}`, `@`, `\.`, `^`, `$`

## 2. Technology Stack

- **Backend:** Flask
- **Regex engine:** Python `re` module
- **OOP:** `Evidence`, `Case`, `Player`, and `DetectiveEngine`
- **Generators:** line-by-line streaming for large log files
- **Pandas:** structured forensics analysis
- **NumPy:** matrix-based CCTV grid analysis
- **Matplotlib:** automatic post-case report charts
- **Persistence:** JSON, pickle, CSV, and append-only notes
- **Frontend:** HTML, CSS, and vanilla JavaScript

## 3. Core Gameplay and Scoring

### Scoring Logic

`Score = (Recall × 500) + (Precision × 300) + Brevity Bonus - Decoy Penalty - Attempt Penalty`

### Rules
1. **Precision** = correct clues found / total matches caught  
2. **Recall** = correct clues found / total target clues  
3. **Brevity Bonus** = up to 50 points for clean, elegant regex  
4. **Decoy Penalty** = minus 40 points per false-positive decoy  
5. **Search Budget** = each search consumes one warrant  
6. **Accusations**:
   - Correct accusation: +20 reputation, +200 points, +500 on final boss
   - Wrong accusation: -20 reputation
7. **Stars**:
   - 3 stars: full recall and full precision
   - 2 stars: strong progress with minor decoys
   - 1 star: partial clues found
   - 0 stars: no valid progress

## 4. Progression of the 8 Playable Cases

| Case | Title | Regex / Tool Focus | Target Evidence | Culprit |
|---|---|---|---|---|
| Case 01 | Operation Dark Rupee | `\d`, character sets, length | Delhi 6-digit PIN codes | Rajesh Oberoi |
| Case 02 | Operation Hawala Wire | Quantifiers and anchors | Active phone lines | Vikram Malhotra |
| Case 03 | The UPI Syndicate | Groups and alternation | Bank UPI handles | Pooja Verma |
| Case 04 | The Midnight Alibi | Dates and 24-hour times | Late-night timestamps | Alok Verma |
| Case 05 | Forensics Lab: Data Breach | Pandas DataFrame | Rogue device telemetry | Karan Saxena |
| Case 06 | CCTV Surveillance Grid | NumPy 8×8 matrix | Thermal camera surge coordinates | Suresh Nair |
| Case 07 | Operation Redacted Shadow | `re.sub()` de-masking | Unmasked secret project codes | Monica Dsouza |
| Case 08 | Final Boss: Vedic Vault | Mixed master challenge | Zero-hour time, architect line, treasury UPI, Vedic key | Dr. Aryan Dev |

## 5. Project Directory Structure

```text
regex_detective/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── game/
│   ├── __init__.py
│   ├── evidence.py
│   ├── engine.py
│   ├── exceptions.py
│   ├── storage.py
│   ├── analytics.py
│   └── vault.py
├── data/
│   ├── cases/
│   ├── evidence/
│   ├── saves/
│   ├── notes/
│   ├── reports/
│   └── leaderboard.csv
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    └── index.html
```

## 6. Local Setup and Quickstart

### Prerequisites
- Python 3.10 or newer
- `pip`

### Installation

1. Go to the project directory:
```powershell
cd "regex_detective"
```

2. Create and activate a virtual environment if needed:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Start the Flask server:
```powershell
python app.py
```

5. Open the app in your browser:
```text
http://127.0.0.1:5000/
```

## 7. REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves dashboard UI or health JSON |
| `/case/<id>` | GET | Returns case briefing, evidence, suspects, and budget |
| `/search` | POST | Validates regex, updates budget, and scores the warrant |
| `/accuse` | POST | Accuses a suspect and updates progression |
| `/case/<id>/reset` | POST | Restores search budget |
| `/case/<id>/report` | GET | Returns case summary and report data |
| `/reports/<file>` | GET | Serves generated report image |
| `/session/save` | POST | Saves player state with pickle |
| `/session/load` | POST | Loads player state from pickle |
| `/session/saves` | GET | Lists available save slots |
| `/leaderboard` | GET | Returns top scores |
| `/notes` | GET / POST | Reads or appends detective notes |

## 8. Viva and Presentation Guide

### Elevator Pitch
Regex Detective is a gamified cybercrime forensic dashboard. Instead of dry regex exercises, students solve 8 narrative cases using Flask, Python `re`, Pandas, NumPy, and Matplotlib. Broad patterns catch realistic decoys and reduce precision, while elegant patterns uncover real clues and unlock stars, charts, and the final Vedic Vault.

### Key Design Decisions
- **Why server-side regex?**  
  To keep regex behavior consistent and to catch invalid patterns safely with custom exceptions.
- **Why sets for scoring?**  
  To compare matches and target clues cleanly and compute precision and recall.
- **Why generators?**  
  To stream large evidence files efficiently.
- **Why multiple storage formats?**  
  JSON for case data, pickle for session saves, CSV for leaderboards, and text for notes.
- **Why Matplotlib?**  
  To generate a visual summary after each case.

### Sample Viva Questions
- What happens if the regex is invalid?  
  The engine catches `re.error` and raises a friendly in-game error.

- How does Case 7 use `re.sub()`?  
  It removes redaction noise and reveals hidden clues.

- What makes the final vault special?  
  It combines multiple regex skills into one multi-stage final challenge.

## 9. License

Developed as a Computer Programming academic mini project. Free to extend for educational use.
