"""Evidence and Case domain models for Regex Detective."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, List, Optional, Set, Tuple, Union

from game.exceptions import EvidenceLoadError


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
        story: str,
        evidence: Union[Evidence, List[Evidence]],
        answers: List[str],
    ) -> None:
        self.title: str = title
        self.story: str = story
        self.evidence: Union[Evidence, List[Evidence]] = evidence
        self.__answers: Set[str] = set(answers)

    @property
    def answer_count(self) -> int:
        """Returns the number of real clues in this case."""
        return len(self.__answers)

    def check(self, found: List[str]) -> Tuple[float, float]:
        """Calculates precision and recall against real answers."""
        found_set = set(found)
        hits = found_set & self.__answers

        precision = len(hits) / len(found_set) if found_set else 0.0
        recall = len(hits) / len(self.__answers) if self.__answers else 0.0

        return precision, recall
