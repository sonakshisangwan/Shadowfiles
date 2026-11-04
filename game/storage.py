"""Storage handling for JSON cases, pickle player saves, CSV leaderboard, and detective notes."""
import csv
from datetime import datetime
import json
from pathlib import Path
import pickle
from typing import Any, Dict, List, Optional, Set

from game.evidence import Case, Evidence
from game.exceptions import CaseNotFoundError, DetectiveError


class Player:
    """Represents the player's cybercrime detective profile and investigation progress."""

    def __init__(
        self,
        name: str = "Rookie Detective",
        reputation: int = 100,
        coins: int = 50,
        current_case_id: str = "case_01",
    ) -> None:
        self.name: str = name
        self.reputation: int = reputation
        self.coins: int = coins
        self.current_case_id: str = current_case_id
        self.score: int = 0
        self.collected_clues: Dict[str, Set[str]] = {}
        self.solved_cases: Set[str] = set()
        self.failed_cases: Set[str] = set()
        self.case_scores: Dict[str, int] = {}

    def add_clues(self, case_id: str, clues: List[str]) -> None:
        """Adds discovered genuine clues for a case."""
        if case_id not in self.collected_clues:
            self.collected_clues[case_id] = set()
        self.collected_clues[case_id].update(clues)

    def get_collected_clues(self, case_id: str) -> List[str]:
        """Returns sorted list of clues collected for a case."""
        return sorted(list(self.collected_clues.get(case_id, set())))

    def record_score(self, case_id: str, points: int) -> None:
        """Updates case score and cumulative detective score."""
        prev = self.case_scores.get(case_id, 0)
        if points > prev:
            diff = points - prev
            self.case_scores[case_id] = points
            self.score += diff

    def penalize_reputation(self, amount: int = 20) -> int:
        """Deducts reputation points for invalid actions or false accusations."""
        self.reputation = max(0, self.reputation - amount)
        return self.reputation

    def reward_reputation(self, amount: int = 20) -> int:
        """Awards reputation points for successful case closures."""
        self.reputation = min(100, self.reputation + amount)
        return self.reputation

    def mark_solved(self, case_id: str) -> None:
        """Marks a case as solved."""
        self.solved_cases.add(case_id)
        self.failed_cases.discard(case_id)

    def mark_failed(self, case_id: str) -> None:
        """Marks a case as failed."""
        self.failed_cases.add(case_id)

    def get_case_status(self, case_id: str) -> str:
        """Returns current investigation status for a case."""
        if case_id in self.solved_cases:
            return "solved"
        if case_id in self.failed_cases:
            return "failed"
        return "in_progress"

    def to_dict(self) -> Dict[str, Any]:
        """Returns player summary dictionary."""
        return {
            "name": self.name,
            "reputation": self.reputation,
            "coins": self.coins,
            "current_case_id": self.current_case_id,
            "score": self.score,
            "solved_cases": sorted(list(self.solved_cases)),
            "failed_cases": sorted(list(self.failed_cases)),
            "case_scores": self.case_scores,
        }


class CaseManager:
    """Manages case loading, caching, persistence, and retrieval from disk and memory."""

    def __init__(self, cases_dir: Optional[Path] = None) -> None:
        if cases_dir is None:
            self.cases_dir = Path(__file__).resolve().parent.parent / "data" / "cases"
        else:
            self.cases_dir = Path(cases_dir)

        self._cases: Dict[str, Case] = {}
        self.load_all_cases()

    def _normalize_id(self, case_id: str) -> str:
        """Normalizes case id strings e.g. '1' -> 'case_01', 'vault' -> 'case_08'."""
        cid = str(case_id).strip().lower()
        if cid in ("vault", "vedic", "vedic_vault", "boss", "finale"):
            return "case_08"
        if cid.isdigit():
            return f"case_{int(cid):02d}"
        if cid.startswith("case_") and cid[5:].isdigit():
            return f"case_{int(cid[5:]):02d}"
        return cid

    def load_case_from_dict(self, data: Dict[str, Any]) -> Case:
        """Creates a Case object from raw dictionary data."""
        ev_name = data.get("evidence_name", f"{data.get('title', 'Case')} Evidence")
        ev_text = data.get("evidence_text", "")
        evidence = Evidence(name=ev_name, content=ev_text)

        return Case(
            case_id=data.get("case_id", "case_01"),
            title=data.get("title", "Untitled Case"),
            briefing=data.get("briefing", ""),
            evidence=evidence,
            expected_clues=data.get("expected_clues", []),
            search_budget=data.get("search_budget", 4),
            difficulty=data.get("difficulty", "Beginner"),
            decoys=data.get("decoys", []),
            suspects=data.get("suspects", []),
            culprit=data.get("culprit"),
        )

    def load_all_cases(self) -> None:
        """Loads all case JSON files from the cases directory."""
        if not self.cases_dir.is_dir():
            return

        for fpath in self.cases_dir.glob("*.json"):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    case = self.load_case_from_dict(data)
                    self._cases[case.case_id] = case
            except Exception:
                continue

    def get_case(self, case_id: str) -> Case:
        """Retrieves a case by ID or normalized alias. Raises CaseNotFoundError if not found."""
        norm_id = self._normalize_id(case_id)
        if norm_id in self._cases:
            return self._cases[norm_id]

        if case_id in self._cases:
            return self._cases[case_id]

        raise CaseNotFoundError(f"Case '{case_id}' was not found in archives.")

    def list_cases(self) -> List[Dict[str, Any]]:
        """Returns summary list of all available cases."""
        result: List[Dict[str, Any]] = []
        for cid in sorted(self._cases.keys()):
            c = self._cases[cid]
            result.append({
                "case_id": c.case_id,
                "title": c.title,
                "difficulty": c.difficulty,
                "search_budget": c.search_budget,
                "remaining_budget": c.remaining_budget,
                "suspects": c.suspects,
            })
        return result

    def reset_case(self, case_id: str) -> Case:
        """Resets the search budget and state for a case."""
        case = self.get_case(case_id)
        case.reset_budget()
        return case

    def save_case_to_json(self, case: Case, target_file: Optional[Path] = None) -> Path:
        """Serializes a case to a JSON file."""
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        out_file = target_file or (self.cases_dir / f"{case.case_id}.json")

        ev_text = case.evidence.content if isinstance(case.evidence, Evidence) else ""
        ev_name = case.evidence.name if isinstance(case.evidence, Evidence) else "Evidence"

        data = {
            "case_id": case.case_id,
            "title": case.title,
            "briefing": case.briefing,
            "difficulty": case.difficulty,
            "search_budget": case.search_budget,
            "remaining_budget": case.remaining_budget,
            "searches_used": case.searches_used,
            "evidence_name": ev_name,
            "evidence_text": ev_text,
            "expected_clues": sorted(list(case.expected_clues)),
            "decoys": sorted(list(case.decoys)),
            "suspects": case.suspects,
            "culprit": case.culprit,
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return out_file


# ==============================================================================
# PICKLE PLAYER SESSION SAVES
# ==============================================================================

def get_saves_dir() -> Path:
    """Returns the path to the saves directory, creating it if needed."""
    saves_dir = Path(__file__).resolve().parent.parent / "data" / "saves"
    saves_dir.mkdir(parents=True, exist_ok=True)
    return saves_dir


def save_player_pickle(player_obj: Player, slot_name: str = "detective_save") -> Path:
    """Saves player session to a local pickle file."""
    saves_dir = get_saves_dir()
    clean_slot = "".join(c for c in slot_name if c.isalnum() or c in ("_", "-")) or "save"
    save_path = saves_dir / f"{clean_slot}.pkl"

    with open(save_path, "wb") as f:
        pickle.dump(player_obj, f)

    return save_path


def load_player_pickle(slot_name: str = "detective_save") -> Optional[Player]:
    """Restores player session from a local pickle file. Returns None if missing or corrupted."""
    saves_dir = get_saves_dir()
    clean_slot = "".join(c for c in slot_name if c.isalnum() or c in ("_", "-")) or "save"
    save_path = saves_dir / f"{clean_slot}.pkl"

    if not save_path.is_file():
        return None

    try:
        with open(save_path, "rb") as f:
            loaded = pickle.load(f)
            if isinstance(loaded, Player):
                return loaded
            return None
    except (pickle.PickleError, EOFError, AttributeError, ValueError, OSError):
        return None


def list_save_slots() -> List[Dict[str, Any]]:
    """Lists all available save slots with file metadata."""
    saves_dir = get_saves_dir()
    slots: List[Dict[str, Any]] = []

    for fpath in saves_dir.glob("*.pkl"):
        stat = fpath.stat()
        slots.append({
            "slot": fpath.stem,
            "filename": fpath.name,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return sorted(slots, key=lambda x: x["modified"], reverse=True)


# ==============================================================================
# CSV LEADERBOARD
# ==============================================================================

LEADERBOARD_FIELDS = [
    "timestamp",
    "player_name",
    "case_id",
    "case_title",
    "score",
    "precision",
    "recall",
    "stars",
    "status",
]


def get_leaderboard_path() -> Path:
    """Returns the path to the leaderboard CSV file."""
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / "leaderboard.csv"


def record_leaderboard_entry(
    player_name: str,
    case_id: str,
    case_title: str,
    score: int,
    precision: float,
    recall: float,
    stars: int,
    status: str = "SOLVED",
) -> Dict[str, Any]:
    """Appends an entry to the CSV leaderboard."""
    csv_path = get_leaderboard_path()
    file_exists = csv_path.is_file()

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_name": player_name,
        "case_id": case_id,
        "case_title": case_title,
        "score": int(score),
        "precision": round(float(precision), 3),
        "recall": round(float(recall), 3),
        "stars": int(stars),
        "status": status.upper(),
    }

    try:
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LEADERBOARD_FIELDS)
            if not file_exists or csv_path.stat().st_size == 0:
                writer.writeheader()
            writer.writerow(entry)
    except OSError:
        pass

    return entry


def get_leaderboard(limit: int = 50) -> List[Dict[str, Any]]:
    """Reads and returns entries from the CSV leaderboard sorted by score descending."""
    csv_path = get_leaderboard_path()
    if not csv_path.is_file() or csv_path.stat().st_size == 0:
        return []

    entries: List[Dict[str, Any]] = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    entries.append({
                        "timestamp": row.get("timestamp", ""),
                        "player_name": row.get("player_name", "Anonymous"),
                        "case_id": row.get("case_id", ""),
                        "case_title": row.get("case_title", ""),
                        "score": int(row.get("score", 0)),
                        "precision": float(row.get("precision", 0.0)),
                        "recall": float(row.get("recall", 0.0)),
                        "stars": int(row.get("stars", 0)),
                        "status": row.get("status", "IN_PROGRESS"),
                    })
                except (ValueError, TypeError):
                    continue
    except OSError:
        return []

    entries.sort(key=lambda x: x["score"], reverse=True)
    return entries[:limit]


# ==============================================================================
# DETECTIVE NOTES (APPEND-ONLY TEXT)
# ==============================================================================

def get_notes_path() -> Path:
    """Returns the path to the notes file, ensuring the directory exists."""
    notes_dir = Path(__file__).resolve().parent.parent / "data" / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    return notes_dir / "detective_notes.txt"


def append_detective_note(
    note: str,
    case_id: str = "case_01",
    author: str = "Rookie Detective",
) -> Dict[str, str]:
    """Appends a new detective field note."""
    notes_path = get_notes_path()
    clean_note = note.strip().replace("\r", "").replace("\n", " ")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry_line = f"[{timestamp}] [{case_id}] ({author}): {clean_note}\n"

    try:
        with open(notes_path, "a", encoding="utf-8") as f:
            f.write(entry_line)
    except OSError:
        pass

    return {
        "timestamp": timestamp,
        "case_id": case_id,
        "author": author,
        "note": clean_note,
    }


def get_detective_notes(case_id: Optional[str] = None) -> List[Dict[str, str]]:
    """Reads detective field notes, optionally filtering by case_id."""
    notes_path = get_notes_path()
    if not notes_path.is_file():
        return []

    notes: List[Dict[str, str]] = []
    try:
        with open(notes_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith("["):
                    continue

                # Format: [2026-11-04 22:30:00] [case_01] (Author): Note text
                try:
                    parts = line.split("] [", 1)
                    if len(parts) == 2:
                        ts = parts[0].lstrip("[")
                        rest = parts[1]
                        cid_part, note_part = rest.split("] (", 1)
                        author_part, text = note_part.split("): ", 1)

                        if case_id and cid_part.strip().lower() != case_id.strip().lower():
                            continue

                        notes.append({
                            "timestamp": ts,
                            "case_id": cid_part,
                            "author": author_part,
                            "note": text,
                        })
                except Exception:
                    continue
    except OSError:
        return []

    return notes


# Singleton manager and active player session
case_manager = CaseManager()
player = Player()
