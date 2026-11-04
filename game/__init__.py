"""Regex Detective Game Package."""
from game.analytics import (
    generate_case_report_chart,
    generate_cctv_evidence_text,
    generate_forensics_evidence_text,
    get_reports_dir,
    unmask_redactions,
)
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
from game.storage import (
    CaseManager,
    Player,
    append_detective_note,
    case_manager,
    get_detective_notes,
    get_leaderboard,
    list_save_slots,
    load_player_pickle,
    player,
    record_leaderboard_entry,
    save_player_pickle,
)
from game.vault import VedicVaultCase, create_vedic_vault_case

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
    "Player",
    "CaseManager",
    "case_manager",
    "player",
    "save_player_pickle",
    "load_player_pickle",
    "list_save_slots",
    "record_leaderboard_entry",
    "get_leaderboard",
    "append_detective_note",
    "get_detective_notes",
    "generate_case_report_chart",
    "get_reports_dir",
    "generate_forensics_evidence_text",
    "generate_cctv_evidence_text",
    "unmask_redactions",
    "VedicVaultCase",
    "create_vedic_vault_case",
]
