"""Regex matching engine, clue verification, and scoring logic for Regex Detective."""
from dataclasses import asdict, dataclass, field
import re
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Union

from game.evidence import Case, Evidence
from game.exceptions import InvalidWarrantError, WarrantBudgetExceeded


@dataclass
class SearchResult:
    """Structured result returned by a warrant search."""

    pattern: str
    matches: List[str]
    correct_matches: List[str]
    false_matches: List[str]
    missed_clues: List[str]
    precision: float
    recall: float
    score: int
    remaining_budget: int
    stars: int = 0
    feedback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON APIs and serialization."""
        return asdict(self)

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)


def calculate_precision(correct_count: int, total_matches: int) -> float:
    """Calculates precision = correct matches / total matches."""
    if total_matches <= 0:
        return 0.0
    return round(correct_count / total_matches, 3)


def calculate_recall(correct_count: int, total_expected: int) -> float:
    """Calculates recall = correct matches / total expected clues."""
    if total_expected <= 0:
        return 0.0
    return round(correct_count / total_expected, 3)


def calculate_stars(precision: float, recall: float) -> int:
    """Awards 0 to 3 stars based on precision and recall."""
    if recall >= 1.0 and precision >= 1.0:
        return 3
    if recall >= 1.0 and precision >= 0.5:
        return 2
    if recall >= 0.5 and precision >= 0.5:
        return 2
    if recall > 0.0:
        return 1
    return 0


def calculate_score(
    pattern: str,
    correct_count: int,
    total_expected: int,
    false_count: int,
    searches_used: int,
) -> int:
    """Calculates score based on recall, precision, brevity bonus, and decoy penalties."""
    if correct_count == 0:
        return 0

    precision = correct_count / (correct_count + false_count)
    recall = correct_count / total_expected if total_expected > 0 else 0.0

    # Base points
    recall_points = int(recall * 500)
    precision_points = int(precision * 300)

    # Penalties
    false_penalty = false_count * 40
    attempt_penalty = max(0, searches_used - 1) * 25

    # Brevity bonus for concise regex (max 50 points when all clues found cleanly)
    pattern_len = len(pattern.strip())
    brevity_bonus = (
        max(0, 50 - pattern_len)
        if (recall >= 1.0 and precision >= 1.0)
        else 0
    )

    total = recall_points + precision_points + brevity_bonus - false_penalty - attempt_penalty
    return max(0, total)


def generate_feedback(
    precision: float, recall: float, false_count: int, missed_count: int
) -> str:
    """Generates user-friendly detective feedback on the warrant results."""
    if recall >= 1.0 and precision >= 1.0:
        return "Flawless warrant! All clues intercepted with zero decoys triggered."
    if recall >= 1.0:
        return (
            f"All clues identified, but {false_count} decoy(s) were caught in the net."
        )
    if recall > 0.0:
        return (
            f"Partial lead: found {int(recall * 100)}% of clues, "
            f"missed {missed_count}, caught {false_count} decoy(s)."
        )
    return "Dead end: your warrant did not uncover any genuine clues."


class DetectiveEngine:
    """Core engine layer that executes regex searches, enforces search budget, and calculates scores."""

    def __init__(
        self,
        evidence: Optional[Evidence] = None,
        case: Optional[Case] = None,
    ) -> None:
        self.case: Optional[Case] = case
        self.evidence: Optional[Evidence] = evidence
        if self.evidence is None and self.case is not None:
            if isinstance(self.case.evidence, Evidence):
                self.evidence = self.case.evidence
            elif isinstance(self.case.evidence, list) and self.case.evidence:
                self.evidence = self.case.evidence[0]

    def set_evidence(self, evidence: Evidence) -> None:
        """Assigns new evidence to the engine."""
        self.evidence = evidence

    def set_case(self, case: Case) -> None:
        """Assigns an investigative case to the engine."""
        self.case = case
        if isinstance(case.evidence, Evidence):
            self.evidence = case.evidence
        elif isinstance(case.evidence, list) and case.evidence:
            self.evidence = case.evidence[0]

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
            raise InvalidWarrantError(f"Invalid warrant! Regex error: {e}") from e

    def search(self, pattern: str) -> List[str]:
        """Executes regex pattern search across the active evidence text."""
        compiled = self.validate_pattern(pattern)
        text = self.get_evidence_text()
        matches = compiled.findall(text)

        flat_matches: List[str] = []
        for m in matches:
            if isinstance(m, tuple):
                flat_matches.extend([item for item in m if item])
            elif isinstance(m, str):
                flat_matches.append(m)

        return flat_matches

    def search_lines(self, pattern: str) -> List[Dict[str, Any]]:
        """Processes evidence line by line using the generator.

        Returns matching lines with their line numbers and matches.
        """
        compiled = self.validate_pattern(pattern)
        matched_lines: List[Dict[str, Any]] = []

        for line_no, line in enumerate(self.get_evidence_lines(), start=1):
            line_matches = compiled.findall(line)
            if line_matches:
                extracted: List[str] = []
                for m in line_matches:
                    if isinstance(m, tuple):
                        extracted.extend([item for item in m if item])
                    elif isinstance(m, str):
                        extracted.append(m)
                if extracted:
                    matched_lines.append({
                        "line_no": line_no,
                        "line": line,
                        "matches": extracted,
                    })

        return matched_lines

    def search_case(
        self,
        pattern: str,
        case: Optional[Case] = None,
    ) -> SearchResult:
        """Executes a warrant search against a case.

        Deducts from search budget, filters decoys, and scores precision/recall.
        """
        active_case = case or self.case
        if active_case is None:
            raise ValueError("No active case assigned to DetectiveEngine.")

        # 1. Enforce search budget
        if active_case.remaining_budget <= 0:
            raise WarrantBudgetExceeded(
                "Search budget exhausted! You have no warrants left for this case."
            )

        # 2. Validate regex pattern
        compiled = self.validate_pattern(pattern)

        # 3. Deduct budget
        remaining = active_case.spend_budget()
        searches_used = active_case.searches_used

        # 4. Extract matches across case evidence
        raw_matches: List[str] = []
        ev_items = (
            active_case.evidence
            if isinstance(active_case.evidence, list)
            else [active_case.evidence] if active_case.evidence else []
        )

        for ev in ev_items:
            if ev is not None:
                found = compiled.findall(ev.content)
                for item in found:
                    if isinstance(item, tuple):
                        raw_matches.extend([x for x in item if x])
                    elif isinstance(item, str):
                        raw_matches.append(item)

        # 5. Use sets for clue and decoy verification
        unique_matches: Set[str] = set(raw_matches)
        correct: Set[str] = unique_matches & active_case.expected_clues
        false_matches: Set[str] = unique_matches - active_case.expected_clues
        missed: Set[str] = active_case.expected_clues - unique_matches

        # 6. Scoring calculations
        precision = calculate_precision(len(correct), len(unique_matches))
        recall = calculate_recall(len(correct), len(active_case.expected_clues))
        score = calculate_score(
            pattern=pattern,
            correct_count=len(correct),
            total_expected=len(active_case.expected_clues),
            false_count=len(false_matches),
            searches_used=searches_used,
        )
        stars = calculate_stars(precision, recall)
        feedback = generate_feedback(
            precision=precision,
            recall=recall,
            false_count=len(false_matches),
            missed_count=len(missed),
        )

        return SearchResult(
            pattern=pattern,
            matches=sorted(list(unique_matches)),
            correct_matches=sorted(list(correct)),
            false_matches=sorted(list(false_matches)),
            missed_clues=sorted(list(missed)),
            precision=precision,
            recall=recall,
            score=score,
            remaining_budget=remaining,
            stars=stars,
            feedback=feedback,
        )


def create_sample_case() -> Case:
    """Helper to generate a realistic sample case for testing and demonstration."""
    log_content = (
        "[2026-11-04 10:14:02] INTERCEPT_NODE_01: Inbound SMS from +91-98765-43210\n"
        "[2026-11-04 10:15:33] Transaction alert: Rs 25,000 sent to shadow.dev@okhdfcbank\n"
        "[2026-11-04 10:18:45] Decoy ping detected from +91-00000-00000 (inactive burner)\n"
        "[2026-11-04 10:20:12] Secondary burner detected: +91-11111-22222 (test sim)\n"
        "[2026-11-04 10:22:10] Legitimate suspect callback to +91-98123-45678\n"
        "[2026-11-04 10:30:00] Location ping: Connaught Place, New Delhi - PIN 110001\n"
    )
    ev = Evidence(name="Cyber Hub Wiretap", content=log_content)
    return Case(
        case_id="case_01",
        title="Operation Hawala Wire",
        briefing="Extract authentic active suspect phone numbers (+91-98XXX-XXXXX), avoiding burner decoys.",
        evidence=ev,
        expected_clues=["+91-98765-43210", "+91-98123-45678"],
        decoys=["+91-00000-00000", "+91-11111-22222"],
        search_budget=3,
        difficulty="Beginner",
    )


def run_demo() -> None:
    """Demonstrates regex searching, decoy filtering, budget tracking, and scoring."""
    case = create_sample_case()
    engine = DetectiveEngine(case=case)

    print("=" * 60)
    print(f"CASE BRIEFING: {case.title} [{case.difficulty}]")
    print(f"{case.briefing}")
    print(f"Initial Search Budget: {case.remaining_budget}")
    print("=" * 60)

    # 1. Search with broad pattern (catches decoys)
    pattern1 = r"\+91-\d{5}-\d{5}"
    print(f"\n[Attempt 1] Broad Warrant: '{pattern1}'")
    res1 = engine.search_case(pattern1)
    print(f"  Matches found: {res1.matches}")
    print(f"  Correct clues: {res1.correct_matches}")
    print(f"  Decoys caught (false matches): {res1.false_matches}")
    print(f"  Precision: {res1.precision:.1%} | Recall: {res1.recall:.1%}")
    print(f"  Score: {res1.score} | Stars: {'*' * res1.stars} ({res1.stars}/3)")
    print(f"  Feedback: {res1.feedback}")
    print(f"  Remaining Budget: {res1.remaining_budget}")

    # 2. Search with refined pattern (filters out decoys)
    pattern2 = r"\+91-98\d{3}-\d{5}"
    print(f"\n[Attempt 2] Refined Warrant: '{pattern2}'")
    res2 = engine.search_case(pattern2)
    print(f"  Matches found: {res2.matches}")
    print(f"  Correct clues: {res2.correct_matches}")
    print(f"  Decoys caught: {res2.false_matches}")
    print(f"  Precision: {res2.precision:.1%} | Recall: {res2.recall:.1%}")
    print(f"  Score: {res2.score} | Stars: {'*' * res2.stars} ({res2.stars}/3)")
    print(f"  Feedback: {res2.feedback}")
    print(f"  Remaining Budget: {res2.remaining_budget}")

    # 3. Test invalid regex error handling
    print("\n[Attempt 3] Testing Malformed Warrant: r'[invalid('")
    try:
        engine.search_case(r"[invalid(")
    except InvalidWarrantError as e:
        print(f"  Expected Error Caught: {e}")

    # 4. Use last budget and test exhaustion
    print("\n[Attempt 3 Retry] Final Warrant Search:")
    res3 = engine.search_case(r"shadow\.dev@\w+")
    print(f"  Matches found: {res3.matches}")
    print(f"  Remaining Budget: {res3.remaining_budget}")

    print("\n[Attempt 4] Testing Exhausted Budget:")
    try:
        engine.search_case(r"\d+")
    except WarrantBudgetExceeded as e:
        print(f"  Expected Budget Exhaustion: {e}")

    print("\n" + "=" * 60)
    print("STEP 3 ENGINE DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
