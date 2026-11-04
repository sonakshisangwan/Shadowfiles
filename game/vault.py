"""Vedic Vault finale challenge module - Final Master Boss Case."""
import re
from typing import Any, Dict, List, Set, Tuple

from game.evidence import Case, Evidence


# Master Clues combining all previous regex techniques
VAULT_CLUES = [
    "2026-11-04 23:59",           # Alibi/Zero-Hour Breach Timestamp
    "+91-98777-12345",            # Architect Secure Phone Line
    "cryptic.master@okhdfcbank",  # Laundering UPI Handle
    "VAULT-OM-108",               # Unmasked Master Vedic Key
]

VAULT_DECOYS = [
    "2026-11-04 12:00",           # Decoy noon heartbeat
    "+91-00000-00000",            # Dead burner decoy
    "test.dummy@fakeupi",         # Sandboxed test UPI
    "VAULT-99",                   # Incomplete decoy key
    "###DECOY-DUMMY-000###",      # Redacted decoy noise
]

VAULT_SUSPECTS = [
    "Dr. Aryan Dev (The Architect)",
    "Vikram Malhotra (Hawala Broker)",
    "Monica Dsouza (Cipher Operative)",
    "Karan Saxena (Forensic Infiltrator)",
]

VAULT_CULPRIT = "Dr. Aryan Dev (The Architect)"


def generate_vault_evidence_text() -> str:
    """Generates the multi-layered Vedic Vault dossier combining all game mechanics."""
    lines: List[str] = [
        "================================================================================",
        "  CLASSIFIED LEVEL-9 DOSSIER: VEDIC VAULT // ZERO-DAY PROTOCOL",
        "  CENTRAL CYBERCRIME BUREAU • APEX INTELLIGENCE ARCHIVE",
        "================================================================================",
        "",
        "--- [CHAMBER 1: PERIMETER GATEWAY & ZERO-HOUR BREACH LOGS] ---",
        "[2026-11-04 12:00] Perimeter Gateway Test Ping: Decoy ping acknowledged (Decoy).",
        "[2026-11-04 22:40] Surveillance confirms outer security barrier arm engaged.",
        "[2026-11-04 23:59] ZERO-HOUR ANOMALY: Mainframe root override at 2026-11-04 23:59.",
        "[2026-11-05 00:01] System timestamp verified by quantum atomic clock sync.",
        "",
        "--- [CHAMBER 2: HAWALA & WIRE COMMUNICATIONS TRANSCRIPT] ---",
        "[TRANSCRIPT] Inbound encrypted satellite voice call routed to +91-98777-12345.",
        "[TRANSCRIPT] Caller voiceprint matches mastermind: Dr. Aryan Dev (The Architect).",
        "[DECOY-SMS] Inactive decoy SIM pinged: +91-00000-00000 (Burner discarded).",
        "[UPI-WIRE] 5,000,000 INR extortion payout routed to: cryptic.master@okhdfcbank.",
        "[UPI-DECOY] Benign test handle flagged by router: test.dummy@fakeupi (IGNORED).",
        "",
        "--- [CHAMBER 3: PANDAS TELEMETRY & NUMPY SENSOR COALESCENCE] ---",
        "[FORENSICS] Rogue node DEV-ARC-8899 synchronized terminal telemetry.",
        "[NUMPY MATRIX] CCTV grid sensor CAM-V9 registered critical 98.6C thermal overload.",
        "[RADAR] High-gain receiver detected encrypted transponder signal near Connaught Place.",
        "",
        "--- [CHAMBER 4: ENCRYPTED VEDIC CIPHER & RE.SUB REDACTION CORE] ---",
        "The root vault lock is shielded by Vedic cipher masking. Redaction tokens are wrapped",
        "in triple hashes '###...###'. Use regex and re.sub() unmasking to extract the master key.",
        "",
        "LOCK CORE RECOVERY BLOCK:",
        "  Noise Packet Alpha: ###DECOY-DUMMY-000### [REDACTED FIREWALL NOISE]",
        "  Noise Packet Beta:  ###VAULT-99### [MALFORMED INCOMPLETE KEY]",
        "  GENUINE VAULT MASTER KEY: ###VAULT-OM-108### [FLAGGED LEVEL-9 MASTER CIPHER]",
        "",
        "================================================================================",
        "INVESTIGATION SUMMARY:",
        "Extract the four master clues to shatter the syndicate:",
        "  1. Zero-hour breach timestamp matching: 2026-11-04 23:\\d{2}",
        "  2. Mastermind priority line: \\+91-98\\d{3}-\\d{5}",
        "  3. Syndicate treasury UPI: \\w+\\.\\w+@okhdfcbank",
        "  4. Master Vedic Vault key: VAULT-[A-Z]{2}-\\d{3}",
        "",
        "FINAL TARGET: Identify and indict the master architect behind the entire conspiracy.",
        "================================================================================",
    ]
    return "\n".join(lines) + "\n"


class VedicVaultCase(Case):
    """Special finale boss case with layered unlock mechanics and high-stakes scoring."""

    def __init__(self) -> None:
        evidence = Evidence(
            name="Vedic Vault Zero-Day Dossier",
            content=generate_vault_evidence_text(),
        )
        super().__init__(
            case_id="case_08",
            title="Final Boss: Vedic Vault",
            briefing=(
                "The Apex Cybercrime Syndicate has locked their final treasury inside the "
                "Vedic Vault. To crack the master lock, combine all your investigative regex "
                "skills: extract the zero-hour breach timestamp, trace the Architect's encrypted "
                "phone line, uncover the treasury UPI handle, and de-mask the root key VAULT-OM-108. "
                "Beware of multi-layered decoys and unmask the mastermind to bring justice!"
            ),
            evidence=evidence,
            expected_clues=VAULT_CLUES,
            decoys=VAULT_DECOYS,
            search_budget=6,
            difficulty="Master / Finale",
            suspects=VAULT_SUSPECTS,
            culprit=VAULT_CULPRIT,
        )

    def check_vault_unlock(self, collected_clues: Set[str]) -> Dict[str, Any]:
        """Calculates vault breach percentage and layer statuses."""
        found = set(collected_clues)
        unlocked_layers = {
            "chamber_1_timestamp": "2026-11-04 23:59" in found,
            "chamber_2_phone": "+91-98777-12345" in found,
            "chamber_3_upi": "cryptic.master@okhdfcbank" in found,
            "chamber_4_cipher_key": "VAULT-OM-108" in found,
        }
        layers_broken = sum(1 for v in unlocked_layers.values() if v)
        percentage = int((layers_broken / 4) * 100)

        return {
            "percentage": percentage,
            "layers_broken": layers_broken,
            "total_layers": 4,
            "layers": unlocked_layers,
            "vault_open": layers_broken == 4,
        }


def create_vedic_vault_case() -> VedicVaultCase:
    """Factory function for instantiating the Vedic Vault finale case."""
    return VedicVaultCase()
