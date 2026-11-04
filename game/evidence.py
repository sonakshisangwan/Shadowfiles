"""Evidence and Case domain models for Regex Detective."""
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union

from game.exceptions import EvidenceLoadError, WarrantBudgetExceeded


class Evidence:
    """Represents a piece of evidence (file or raw text) for investigation."""

    def __init__(
        self,
        name: str,
        filepath: Optional[str] = None,
        content: Optional[str] = None,
    ) -> None:
        self.name: str = name
        self.filepath: Optional[str] = str(filepath) if filepath else None
        self._content: Optional[str] = content

        # Pre-load content if a filepath is provided and no raw content was passed
        if self._content is None and self.filepath is not None:
            self.load()

    def load(self) -> str:
        """Safely loads text from the evidence file path."""
        if not self.filepath:
            raise EvidenceLoadError(f"No filepath provided for evidence '{self.name}'.")

        path = Path(self.filepath)
        if not path.is_file():
            raise EvidenceLoadError(f"Evidence file not found: {self.filepath}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                self._content = f.read()
            return self._content
        except OSError as e:
            raise EvidenceLoadError(
                f"Failed to read evidence file '{self.filepath}': {e}"
            ) from e

    @property
    def content(self) -> str:
        """Returns the full text content, loading from disk if necessary."""
        if self._content is None:
            if self.filepath:
                self.load()
            else:
                self._content = ""
        return self._content

    def preview(self, max_chars: int = 150) -> str:
        """Returns a trimmed preview of the evidence text."""
        text = self.content.strip()
        if len(text) <= max_chars:
            return text
        return f"{text[:max_chars]}..."

    def lines(self) -> Generator[str, None, None]:
        """Generator yielding evidence line by line."""
        if self.filepath and Path(self.filepath).is_file():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    for line in f:
                        yield line.rstrip("\r\n")
            except OSError as e:
                raise EvidenceLoadError(
                    f"Failed streaming from '{self.filepath}': {e}"
                ) from e
        else:
            for line in self.content.splitlines():
                yield line

    def describe(self) -> str:
        """Returns a human-readable description of the evidence source."""
        source = f"file '{self.filepath}'" if self.filepath else "in-memory text"
        return f"[Evidence: {self.name}] ({source})"

    def __repr__(self) -> str:
        return f"Evidence(name={self.name!r}, filepath={self.filepath!r})"


class EmailEvidence(Evidence):
    """Specialized evidence representing an email inbox dump or header fragment."""

    def describe(self) -> str:
        return f"[Email Dump: {self.name}]"


class ChatEvidence(Evidence):
    """Specialized evidence representing intercepted instant messages / chat logs."""

    def describe(self) -> str:
        return f"[Chat Log: {self.name}]"


class Case:
    """Represents an investigative case with briefing, evidence, and answer keys."""

    def __init__(
        self,
        title: str,
        story: str = "",
        evidence: Optional[Union[Evidence, List[Evidence]]] = None,
        answers: Optional[List[str]] = None,
        *,
        case_id: str = "case_01",
        briefing: Optional[str] = None,
        expected_clues: Optional[List[str]] = None,
        search_budget: int = 5,
        difficulty: str = "Beginner",
        decoys: Optional[List[str]] = None,
        suspects: Optional[List[str]] = None,
        culprit: Optional[str] = None,
    ) -> None:
        self.case_id: str = case_id
        self.title: str = title
        self.story: str = briefing if briefing is not None else story
        self.briefing: str = self.story
        self.evidence: Union[Evidence, List[Evidence]] = evidence if evidence is not None else []

        clues = expected_clues if expected_clues is not None else (answers or [])
        self.expected_clues: Set[str] = set(clues)
        self.__answers: Set[str] = self.expected_clues
        self.decoys: Set[str] = set(decoys or [])
        self.suspects: List[str] = suspects or []
        self.culprit: Optional[str] = culprit

        self.search_budget: int = max(1, search_budget)
        self.remaining_budget: int = self.search_budget
        self.searches_used: int = 0
        self.difficulty: str = difficulty

    @property
    def answer_count(self) -> int:
        """Returns the number of real clues in this case."""
        return len(self.expected_clues)

    def spend_budget(self) -> int:
        """Deducts one search warrant from the budget. Raises if budget exhausted."""
        if self.remaining_budget <= 0:
            raise WarrantBudgetExceeded("Search budget exhausted! No warrants remaining.")
        self.remaining_budget -= 1
        self.searches_used += 1
        return self.remaining_budget

    def reset_budget(self) -> None:
        """Resets the search budget to its initial limit."""
        self.remaining_budget = self.search_budget
        self.searches_used = 0

    def check(self, found: List[str]) -> Tuple[float, float]:
        """Calculates precision and recall against real answers."""
        found_set = set(found)
        hits = found_set & self.expected_clues

        precision = len(hits) / len(found_set) if found_set else 0.0
        recall = len(hits) / len(self.expected_clues) if self.expected_clues else 0.0

        return precision, recall

    def to_dict(self) -> Dict[str, Any]:
        """Serializes case metadata for API or UI consumption."""
        ev_names = (
            [e.name for e in self.evidence]
            if isinstance(self.evidence, list)
            else [self.evidence.name] if self.evidence else []
        )
        return {
            "case_id": self.case_id,
            "title": self.title,
            "briefing": self.briefing,
            "evidence_sources": ev_names,
            "difficulty": self.difficulty,
            "search_budget": self.search_budget,
            "remaining_budget": self.remaining_budget,
            "searches_used": self.searches_used,
            "clues_count": len(self.expected_clues),
            "suspects": self.suspects,
        }

    def __repr__(self) -> str:
        return f"Case(id={self.case_id!r}, title={self.title!r}, budget={self.remaining_budget}/{self.search_budget})"
