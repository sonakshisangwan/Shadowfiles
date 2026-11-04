"""Custom exceptions for Regex Detective."""

class DetectiveError(Exception):
    """Base class for all game errors."""

class InvalidWarrantError(DetectiveError):
    """Player's regex is invalid or syntax error."""

class WarrantBudgetExceeded(DetectiveError):
    """Player used all search attempts."""

class WrongAccusationError(DetectiveError):
    """Player accused the wrong suspect."""
