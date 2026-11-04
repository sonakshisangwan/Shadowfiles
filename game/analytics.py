"""Analytics, Forensics Lab (pandas), CCTV Grid (numpy), and Matplotlib Report Generation."""
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import re

import matplotlib
matplotlib.use("Agg")  # Headless backend for web server safety
import matplotlib.pyplot as plt
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
    return pd.DataFrame(data)


def generate_forensics_evidence_text(csv_path: Optional[Path] = None) -> str:
    """Loads or creates the forensics DataFrame and formats it into clean evidence text."""
    df = create_forensics_dataset()

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
        "Compromised audit logs tie rogue device activity directly to operator: Karan Saxena.\n"
    )

    return header + table_str + footer


# ==============================================================================
# 2. NUMPY CCTV SURVEILLANCE GRID
# ==============================================================================

def create_cctv_matrix() -> Tuple[np.ndarray, List[str]]:
    """Creates an 8x8 NumPy matrix representing thermal surveillance sensors."""
    rng = np.random.default_rng(seed=42)
    grid = rng.uniform(20.0, 25.0, size=(8, 8))

    # Thermal surges (>85C)
    grid[0, 3] = 92.4  # CAM-A4
    grid[1, 1] = 88.7  # CAM-B2
    grid[3, 2] = 94.1  # CAM-D3

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
        "Extract coordinates matching 'CAM-[A-H][1-8]' where temperature exceeds 85C.",
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
    return re.sub(r"#{3,}([^#\n]+)#{3,}", r"\1", text)


# ==============================================================================
# 4. MATPLOTLIB INVESTIGATION REPORT GENERATION
# ==============================================================================

def get_reports_dir() -> Path:
    """Returns the reports directory path, creating it if needed."""
    reports_dir = Path(__file__).resolve().parent.parent / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def generate_case_report_chart(
    case_id: str,
    case_title: str,
    score: int,
    stars: int,
    precision: float,
    recall: float,
    correct_count: int,
    false_count: int,
    searches_used: int,
    remaining_budget: int,
    status: str = "SOLVED",
    output_dir: Optional[Path] = None,
) -> Tuple[Path, Dict[str, Any]]:
    """Generates and saves a clean, visual case investigation report chart using Matplotlib."""
    reports_dir = output_dir or get_reports_dir()
    clean_id = str(case_id).strip().lower()
    out_file = reports_dir / f"{clean_id}_report.png"

    # Soft, cozy detective aesthetic colors
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.4), facecolor="#fff8fa")
    fig.patch.set_facecolor("#fff8fa")

    # 1. Left Subplot: Pattern Accuracy (Precision vs Recall)
    metrics = ["Precision", "Recall"]
    values = [round(precision * 100, 1), round(recall * 100, 1)]
    colors_acc = ["#d85d7f", "#489379"]

    ax1.set_facecolor("#ffffff")
    bars1 = ax1.bar(metrics, values, color=colors_acc, width=0.45, edgecolor="#f4d3df", linewidth=1.5)
    ax1.set_ylim(0, 115)
    ax1.set_ylabel("Accuracy Percentage (%)", fontsize=10, color="#3d2f38", fontweight="bold")
    ax1.set_title("Warrant Accuracy", fontsize=11, color="#d85d7f", fontweight="bold", pad=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.3, color="#d85d7f")
    ax1.tick_params(colors="#3d2f38", labelsize=9)

    for spine in ax1.spines.values():
        spine.set_color("#f4d3df")

    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(
            f"{h:.0f}%",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#3d2f38",
        )

    # 2. Right Subplot: Clues & Warrant Resources
    categories = ["Clues Found", "Decoys Triggered", "Warrants Used", "Warrants Left"]
    counts = [correct_count, false_count, searches_used, remaining_budget]
    colors_res = ["#489379", "#d97757", "#d85d7f", "#bca5b2"]

    ax2.set_facecolor("#ffffff")
    bars2 = ax2.bar(categories, counts, color=colors_res, width=0.55, edgecolor="#f4d3df", linewidth=1.5)
    max_c = max(counts) if counts and max(counts) > 0 else 4
    ax2.set_ylim(0, max_c + 2.5)
    ax2.set_ylabel("Count", fontsize=10, color="#3d2f38", fontweight="bold")
    ax2.set_title("Evidence & Budget Allocation", fontsize=11, color="#d85d7f", fontweight="bold", pad=10)
    ax2.grid(axis="y", linestyle="--", alpha=0.3, color="#d85d7f")
    ax2.tick_params(colors="#3d2f38", labelsize=8.5)

    for spine in ax2.spines.values():
        spine.set_color("#f4d3df")

    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(
            f"{int(h)}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#3d2f38",
        )

    # Suptitle
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    star_str = "★" * stars + "☆" * (3 - stars)
    supt = f"INVESTIGATION REPORT: {case_title} [{status.upper()}]\nScore: {score} pts  |  Rating: {star_str}  |  {timestamp_str}"
    fig.suptitle(supt, fontsize=12, fontweight="bold", color="#3d2f38", y=0.98)

    plt.tight_layout()
    fig.subplots_adjust(top=0.82)
    plt.savefig(out_file, dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    summary_data: Dict[str, Any] = {
        "case_id": clean_id,
        "case_title": case_title,
        "status": status.upper(),
        "score": int(score),
        "stars": int(stars),
        "precision": float(precision),
        "recall": float(recall),
        "correct_count": int(correct_count),
        "false_count": int(false_count),
        "searches_used": int(searches_used),
        "remaining_budget": int(remaining_budget),
        "report_filename": out_file.name,
        "report_url": f"/reports/{out_file.name}",
        "timestamp": timestamp_str,
    }

    return out_file, summary_data
