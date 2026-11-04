"""Custom exceptions for Regex Detective / Shadowfiles."""


class DetectiveError(Exception):
    """Base exception for all game errors."""
    pass


class InvalidWarrantError(DetectiveError):
    """Raised when regex pattern is invalid, empty, or malformed."""
    pass


class CaseNotFoundError(DetectiveError):
    """Raised when a requested case file cannot be found."""
    pass


class EvidenceLoadError(DetectiveError):
    """Raised when evidence file or content cannot be loaded."""
    pass


class WarrantBudgetExceeded(DetectiveError):
    """Raised when player exceeds allotted search warrants/attempts."""
    pass


class WrongAccusationError(DetectiveError):
    """Raised when player accuses the wrong suspect."""
    pass
