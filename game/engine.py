"""Regex matching engine and scoring logic for Regex Detective."""
import re
from typing import Generator, List, Optional

from game.evidence import Evidence
from game.exceptions import InvalidWarrantError


class DetectiveEngine:
    """Core engine layer that wraps evidence inspection and regex operations."""

    def __init__(self, evidence: Optional[Evidence] = None) -> None:
        self.evidence: Optional[Evidence] = evidence

    def set_evidence(self, evidence: Evidence) -> None:
        """Assigns new evidence to the engine."""
        self.evidence = evidence

    def get_evidence_text(self) -> str:
        """Returns the full text of the active evidence."""
        if self.evidence is None:
            return ""
        return self.evidence.content

    def get_evidence_lines(self) -> Generator[str, None, None]:
        """Yields lines from the active evidence generator."""
        if self.evidence is not None:
            yield from self.evidence.lines()

    def preview_evidence(self, max_chars: int = 150) -> str:
        """Returns a trimmed preview of the active evidence."""
        if self.evidence is None:
            return "No evidence loaded."
        return self.evidence.preview(max_chars=max_chars)

    def validate_pattern(self, pattern: str) -> re.Pattern:
        """Validates that a regex pattern compiles without syntax errors."""
        if not pattern or not pattern.strip():
            raise InvalidWarrantError("Invalid warrant! Search pattern cannot be empty.")
        try:
            return re.compile(pattern)
        except re.error as e:
            raise InvalidWarrantError(f"Invalid warrant! Regex syntax error: {e}") from e

    def search(self, pattern: str) -> List[str]:
        """Executes regex pattern search across the evidence text."""
        compiled = self.validate_pattern(pattern)
        text = self.get_evidence_text()
        matches = compiled.findall(text)

        # Flatten match tuples if groups were used in regex
        flat_matches: List[str] = []
        for m in matches:
            if isinstance(m, tuple):
                flat_matches.extend([item for item in m if item])
            elif isinstance(m, str):
                flat_matches.append(m)

        return flat_matches


def run_demo() -> None:
    """Quick demonstration and self-test of Evidence and DetectiveEngine."""
    sample_text = (
        "--- CYBER POLICE TRANSCRIPT [NEW DELHI] ---\n"
        "[22:04] Officer: Track all incoming transactions.\n"
        "[22:05] Intercept: +91-98765-43210 transferred INR 50,000 to shadow@upi\n"
        "[22:06] Decoy alert: +91-00000-00000 (inactive)\n"
        "[22:07] Suspect IP: 192.168.1.45"
    )

    print("=== Step 2 Demo: Evidence & Detective Engine ===")
    evidence = Evidence(name="Cyber Hub Logs", content=sample_text)
    engine = DetectiveEngine(evidence=evidence)

    print(f"Evidence loaded: {evidence.describe()}")
    print(f"Preview: {engine.preview_evidence(70)}")
    print("\nStreaming lines via generator:")
    for idx, line in enumerate(engine.get_evidence_lines(), start=1):
        print(f"  {idx}: {line}")

    # Test regex validation and basic match
    phone_pattern = r"\+91-\d{5}-\d{5}"
    print(f"\nExecuting warrant for phone numbers: '{phone_pattern}'")
    results = engine.search(phone_pattern)
    print(f"Found matches: {results}")

    # Test invalid regex warrant catching
    try:
        engine.validate_pattern(r"[invalid(regex")
    except InvalidWarrantError as e:
        print(f"\nCaptured expected warrant error: {e}")


if __name__ == "__main__":
    run_demo()
