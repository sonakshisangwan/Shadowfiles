"""Analytics, Forensics Lab (pandas), CCTV Grid (numpy), and re.sub cipher utilities."""
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

import numpy as np
import pandas as pd


# ==============================================================================
# 1. PANDAS FORENSICS LAB
# ==============================================================================

def create_forensics_dataset() -> pd.DataFrame:
    """Creates a realistic tabular dataframe representing banking terminal access logs."""
    data = {
        "log_id": [101, 102, 103, 104, 105, 106, 107, 108],
        "timestamp": [
            "2026-11-04 14:02:11",
            "2026-11-04 14:05:44",
            "2026-11-04 14:12:30",
            "2026-11-04 14:18:02",
            "2026-11-04 14:25:51",
            "2026-11-04 14:31:10",
            "2026-11-04 14:40:00",
            "2026-11-04 14:55:18",
        ],
        "device_id": [
            "SYS-SRV-1001",
            "DEV-ROK-9921",
            "DEV-999",
            "DEV-SHD-4102",
            "SYS-SRV-1002",
            "DEV-TEST-01",
            "DEV-ROK-9921",
            "DEV-SHD-4102",
        ],
        "ip_address": [
            "10.0.1.10",
            "192.168.1.105",
            "192.168.1.200",
            "10.0.4.55",
            "10.0.1.12",
            "127.0.0.1",
            "192.168.1.105",
            "10.0.4.55",
        ],
        "action": [
            "HEARTBEAT",
            "EXFIL_DATA",
            "PING",
            "UNAUTH_DUMP",
            "HEARTBEAT",
            "TEST_ECHO",
            "SESSION_CLOSE",
            "SESSION_CLOSE",
        ],
        "status": [
            "SUCCESS",
            "FLAGGED",
            "DROPPED",
            "FLAGGED",
            "SUCCESS",
            "IGNORED",
            "SUCCESS",
            "SUCCESS",
        ],
        "operator": [
            "SystemDaemon",
            "Karan Saxena",
            "Unknown",
            "Karan Saxena",
            "SystemDaemon",
            "Tester",
            "Karan Saxena",
            "Karan Saxena",
        ],
    }
    df = pd.DataFrame(data)
    return df


def generate_forensics_evidence_text(csv_path: Optional[Path] = None) -> str:
    """Loads or creates the forensics DataFrame and formats it into clean evidence text."""
    df = create_forensics_dataset()
    
    # Save to CSV in data/evidence/ if not already present
    evidence_dir = Path(__file__).resolve().parent.parent / "data" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    csv_file = evidence_dir / "forensics_logs.csv"
    if not csv_file.exists():
        df.to_csv(csv_file, index=False)

    summary_counts = df["action"].value_counts().to_dict()
    flagged_df = df[df["status"] == "FLAGGED"]

    header = (
        "=== CYBER FORENSICS LAB: TABULAR TERMINAL TELEMETRY (PANDAS ENGINE) ===\n"
        f"Total Log Records: {len(df)} | Anomalous Flagged: {len(flagged_df)}\n"
        f"Action Distribution: {summary_counts}\n"
        + "=" * 72 + "\n"
    )
    
    table_str = df[["timestamp", "device_id", "ip_address", "action", "status", "operator"]].to_string(index=False)
    
    footer = (
        "\n" + "=" * 72 + "\n"
        "FORENSIC ANALYST NOTE:\n"
        "Only devices following the rogue pattern 'DEV-[A-Z]{3}-\\d{4}' with FLAGGED\n"
        "exfiltration status belong to the perpetrator. Ignore internal 'SYS-' nodes\n"
        "and malformed device tags like DEV-999 or DEV-TEST-01.\n"
        f"Compromised audit logs tie rogue device activity directly to operator: Karan Saxena.\n"
    )
    
    return header + table_str + footer


# ==============================================================================
# 2. NUMPY CCTV SURVEILLANCE GRID
# ==============================================================================

def create_cctv_matrix() -> Tuple[np.ndarray, List[str]]:
    """Creates an 8x8 NumPy matrix representing thermal surveillance sensors."""
    # Seed for deterministic reproducible surveillance readings
    rng = np.random.default_rng(seed=42)
    # Ambient room temperature in Celsius: 20.0C to 25.0C
    grid = rng.uniform(20.0, 25.0, size=(8, 8))

    # Inject specific thermal surges (>85C) corresponding to breached locations
    # (Row 0, Col 3) -> CAM-A4 = 92.4C
    # (Row 1, Col 1) -> CAM-B2 = 88.7C
    # (Row 3, Col 2) -> CAM-D3 = 94.1C
    grid[0, 3] = 92.4
    grid[1, 1] = 88.7
    grid[3, 2] = 94.1

    hot_cams = ["CAM-A4", "CAM-B2", "CAM-D3"]
    return grid, hot_cams


def generate_cctv_evidence_text() -> str:
    """Converts the NumPy CCTV matrix into formatted surveillance grid text."""
    grid, hot_cams = create_cctv_matrix()
    row_labels = ["A", "B", "C", "D", "E", "F", "G", "H"]
    
    mean_temp = float(np.mean(grid))
    max_temp = float(np.max(grid))

    lines: List[str] = [
        "=== CCTV SURVEILLANCE MATRIX: 8x8 THERMAL HEAT GRID (NUMPY ENGINE) ===",
        f"Matrix Shape: {grid.shape} | Sensors: {grid.size} | Mean Temp: {mean_temp:.1f}C | Peak Surge: {max_temp:.1f}C",
        "Threshold Alert Level: High (>85.0C indicates active physical intrusion)",
        "-" * 72,
    ]

    for r_idx, r_label in enumerate(row_labels):
        cells: List[str] = []
        for c_idx in range(8):
            val = grid[r_idx, c_idx]
            cam_tag = f"CAM-{r_label}{c_idx + 1}"
            if val > 85.0:
                cells.append(f"{cam_tag}: {val:.1f}C [HOT]")
            else:
                cells.append(f"{cam_tag}: {val:.1f}C")
        lines.append(f"[Row {r_label}] " + " | ".join(cells[:4]))
        lines.append(f"        " + " | ".join(cells[4:]))

    lines.extend([
        "-" * 72,
        "CCTV OPERATOR LOG:",
        "Intrusion alarm detected heat surges across 3 distinct matrix coordinates.",
        f"Extract coordinates matching 'CAM-[A-H][1-8]' where temperature exceeds 85C.",
        "Facial recognition at CAM-A4 and CAM-D3 matched suspect 'Suresh Nair'.",
    ])

    return "\n".join(lines) + "\n"


# ==============================================================================
# 3. RE.SUB CIPHER & REDACTION UTILITY
# ==============================================================================

def apply_re_sub(pattern: str, replacement: str, text: str) -> str:
    """Applies regex substitution to uncover or transform redacted text."""
    try:
        compiled = re.compile(pattern)
        return compiled.sub(replacement, text)
    except re.error:
        return text


def unmask_redactions(text: str) -> str:
    """Utility that strips redaction noise tokens from text."""
    # Removes surrounding triple hashes e.g. ###CODE-ALPHA-42### -> CODE-ALPHA-42
    cleaned = re.sub(r"#{3,}([^#\n]+)#{3,}", r"\1", text)
    return cleaned
