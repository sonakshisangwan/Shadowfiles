"""Storage handling for JSON cases, player profiles, and session state."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from game.evidence import Case, Evidence
from game.exceptions import CaseNotFoundError


class Player:
    """Represents the player's cybercrime detective profile and investigation progress."""

    def __init__(self, name: str = "Rookie Detective", reputation: int = 100) -> None:
        self.name: str = name
        self.reputation: int = reputation
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
            "score": self.score,
            "solved_cases": sorted(list(self.solved_cases)),
            "failed_cases": sorted(list(self.failed_cases)),
            "case_scores": self.case_scores,
        }


class CaseManager:
    """Manages case loading, caching, and retrieval from disk and memory."""

    def __init__(self, cases_dir: Optional[Path] = None) -> None:
        if cases_dir is None:
            self.cases_dir = Path(__file__).resolve().parent.parent / "data" / "cases"
        else:
            self.cases_dir = Path(cases_dir)

        self._cases: Dict[str, Case] = {}
        self.load_all_cases()

    def _normalize_id(self, case_id: str) -> str:
        """Normalizes case id strings e.g. '1' -> 'case_01', 'case_1' -> 'case_01'."""
        cid = str(case_id).strip().lower()
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

        # Try direct match
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


# Singleton manager and default player session for backend runtime
case_manager = CaseManager()
player = Player()
