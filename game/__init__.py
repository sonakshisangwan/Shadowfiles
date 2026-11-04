"""Regex Detective Game Package."""
from game.engine import DetectiveEngine, SearchResult
from game.evidence import Case, ChatEvidence, EmailEvidence, Evidence
from game.exceptions import (
    CaseNotFoundError,
    DetectiveError,
    EvidenceLoadError,
    InvalidWarrantError,
    WarrantBudgetExceeded,
    WrongAccusationError,
)

__all__ = [
    "Evidence",
    "EmailEvidence",
    "ChatEvidence",
    "Case",
    "DetectiveEngine",
    "SearchResult",
    "DetectiveError",
    "InvalidWarrantError",
    "CaseNotFoundError",
    "EvidenceLoadError",
    "WarrantBudgetExceeded",
    "WrongAccusationError",
]
