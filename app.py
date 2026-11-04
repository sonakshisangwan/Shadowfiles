from typing import Any, Dict
from flask import Flask, jsonify, render_template, request, send_from_directory

from game.analytics import generate_case_report_chart, get_reports_dir
from game.engine import DetectiveEngine
from game.exceptions import (
    CaseNotFoundError,
    InvalidWarrantError,
    WarrantBudgetExceeded,
)
from game.storage import (
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

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """Renders the detective game frontend for web browsers, or JSON for API clients."""
    if "text/html" in request.headers.get("Accept", ""):
        return render_template("index.html")

    return jsonify({
        "app": "Regex Detective / Shadowfiles",
        "status": "online",
        "message": "Cybercrime Bureau is active. Access /case/<id> to inspect an active case file.",
        "player": player.to_dict(),
        "available_cases": case_manager.list_cases(),
    }), 200


@app.route("/play", methods=["GET"])
@app.route("/game", methods=["GET"])
def play():
    """Dedicated game interface route."""
    return render_template("index.html")


@app.route("/case/<case_id>", methods=["GET"])
def get_case(case_id: str):
    """Fetches details, evidence preview, and investigation progress for a specific case."""
    try:
        case = case_manager.get_case(case_id)
    except CaseNotFoundError as e:
        return jsonify({
            "success": False,
            "error": "CaseNotFoundError",
            "message": str(e),
        }), 404

    evidence_preview = case.evidence.preview(250) if case.evidence else ""
    evidence_text = case.evidence.content if case.evidence else ""

    vault_status = None
    if case.case_id == "case_08":
        collected = set(player.get_collected_clues(case.case_id))
        unlocked = {
            "Chamber 1 (Zero-Hour Timestamp)": "2026-11-04 23:59" in collected,
            "Chamber 2 (Architect Secure Line)": "+91-98777-12345" in collected,
            "Chamber 3 (Syndicate Treasury UPI)": "cryptic.master@okhdfcbank" in collected,
            "Chamber 4 (Master Vedic Lock Key)": "VAULT-OM-108" in collected,
        }
        broken = sum(1 for v in unlocked.values() if v)
        vault_status = {
            "layers_unlocked": broken,
            "total_layers": 4,
            "percentage": int((broken / 4) * 100),
            "vault_open": broken == 4,
            "chambers": unlocked,
        }

    return jsonify({
        "success": True,
        "case_id": case.case_id,
        "title": case.title,
        "briefing": case.briefing,
        "difficulty": case.difficulty,
        "evidence_preview": evidence_preview,
        "evidence_text": evidence_text,
        "search_budget": case.search_budget,
        "remaining_budget": case.remaining_budget,
        "searches_used": case.searches_used,
        "suspects": case.suspects,
        "collected_clues": player.get_collected_clues(case.case_id),
        "case_score": player.case_scores.get(case.case_id, 0),
        "status": player.get_case_status(case.case_id),
        "player_reputation": player.reputation,
        "player_coins": player.coins,
        "vault_status": vault_status,
    }), 200


@app.route("/case/<case_id>/reset", methods=["POST"])
def reset_case(case_id: str):
    """Resets the search budget for a case."""
    try:
        case = case_manager.reset_case(case_id)
        return jsonify({
            "success": True,
            "case_id": case.case_id,
            "message": f"Warrants and budget for case '{case.case_id}' have been reset.",
            "remaining_budget": case.remaining_budget,
        }), 200
    except CaseNotFoundError as e:
        return jsonify({
            "success": False,
            "error": "CaseNotFoundError",
            "message": str(e),
        }), 404


@app.route("/case/<case_id>/save", methods=["POST"])
def save_case_state(case_id: str):
    """Persists current case state to JSON file."""
    try:
        case = case_manager.get_case(case_id)
        out_path = case_manager.save_case_to_json(case)
        return jsonify({
            "success": True,
            "case_id": case.case_id,
            "message": f"Case state persisted to JSON: {out_path.name}",
        }), 200
    except CaseNotFoundError as e:
        return jsonify({
            "success": False,
            "error": "CaseNotFoundError",
            "message": str(e),
        }), 404


@app.route("/search", methods=["POST"])
def search():
    """Runs a regex warrant against a case evidence, updates budget, and returns score."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    case_id: str = data.get("case_id", "case_01")
    pattern: str = data.get("pattern", "")

    try:
        case = case_manager.get_case(case_id)
    except CaseNotFoundError as e:
        return jsonify({
            "success": False,
            "error": "CaseNotFoundError",
            "message": str(e),
        }), 404

    if not pattern or not str(pattern).strip():
        return jsonify({
            "success": False,
            "error": "InvalidWarrantError",
            "message": "Invalid warrant! Search pattern cannot be empty.",
            "remaining_budget": case.remaining_budget,
        }), 400

    engine = DetectiveEngine(case=case)
    try:
        result = engine.search_case(pattern=pattern)
    except InvalidWarrantError as e:
        return jsonify({
            "success": False,
            "error": "InvalidWarrantError",
            "message": str(e),
            "remaining_budget": case.remaining_budget,
        }), 400
    except WarrantBudgetExceeded as e:
        return jsonify({
            "success": False,
            "error": "WarrantBudgetExceeded",
            "message": str(e),
            "remaining_budget": 0,
        }), 400

    # Record discovered clues and high score
    if result.correct_matches:
        player.add_clues(case.case_id, result.correct_matches)
    player.record_score(case.case_id, result.score)

    payload = result.to_dict()
    payload["success"] = True
    payload["case_id"] = case.case_id
    payload["collected_clues"] = player.get_collected_clues(case.case_id)
    payload["total_score"] = player.score
    payload["player_reputation"] = player.reputation
    payload["player_coins"] = player.coins

    return jsonify(payload), 200


@app.route("/accuse", methods=["POST"])
def accuse():
    """Submits a suspect accusation, evaluating culprit match and updating reputation."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    case_id: str = data.get("case_id", "case_01")
    suspect: str = (data.get("suspect") or data.get("accusation") or "").strip()

    try:
        case = case_manager.get_case(case_id)
    except CaseNotFoundError as e:
        return jsonify({
            "success": False,
            "error": "CaseNotFoundError",
            "message": str(e),
        }), 404

    if not suspect:
        return jsonify({
            "success": False,
            "error": "InvalidAccusationError",
            "message": "You must specify a suspect to submit a formal accusation.",
        }), 400

    if not case.culprit:
        return jsonify({
            "success": False,
            "error": "InvalidAccusationError",
            "message": f"Case '{case.case_id}' does not have a designated culprit.",
        }), 400

    is_correct = suspect.lower() == case.culprit.lower()
    is_vault = case.case_id == "case_08"

    if is_correct:
        player.mark_solved(case.case_id)
        player.reward_reputation(30 if is_vault else 20)
        player.coins += 50 if is_vault else 25
        bonus_points = 500 if is_vault else 200
        player.score += bonus_points

        # Record to CSV Leaderboard
        record_leaderboard_entry(
            player_name=player.name,
            case_id=case.case_id,
            case_title=case.title,
            score=player.score,
            precision=1.0,
            recall=1.0,
            stars=3,
            status="MASTER_SOLVED" if is_vault else "SOLVED",
        )

        status = "solved"
        if is_vault:
            message = (
                f"👑 VEDIC VAULT BREACHED! Mastermind {case.culprit} apprehended! "
                "The Apex Cybercrime Syndicate has fallen. You are now a Master Cybercrime Detective!"
            )
        else:
            message = f"Case Solved! {case.culprit} has been arrested and confessed."
    else:
        player.penalize_reputation(20)
        if player.reputation <= 0:
            player.mark_failed(case.case_id)
            status = "failed"
            message = (
                f"Wrong accusation! {suspect} is innocent. Detective reputation collapsed. Case failed!"
            )
        else:
            status = "in_progress"
            message = (
                f"Wrong accusation! {suspect} has a solid alibi. Reputation penalized by 20 points."
            )

        # Record failed attempt to CSV Leaderboard
        record_leaderboard_entry(
            player_name=player.name,
            case_id=case.case_id,
            case_title=case.title,
            score=player.score,
            precision=0.0,
            recall=0.0,
            stars=0,
            status="FAILED" if status == "failed" else "WRONG_ACCUSATION",
        )

    # Generate visual investigation report chart with Matplotlib
    clues_found = len(player.get_collected_clues(case.case_id))
    total_clues = len(case.expected_clues)
    rec = clues_found / total_clues if total_clues > 0 else 0.0
    stars = 3 if is_correct else (1 if clues_found > 0 else 0)

    try:
        report_file, report_summary = generate_case_report_chart(
            case_id=case.case_id,
            case_title=case.title,
            score=player.score,
            stars=stars,
            precision=1.0 if is_correct else 0.0,
            recall=rec,
            correct_count=clues_found,
            false_count=0 if is_correct else 1,
            searches_used=case.searches_used,
            remaining_budget=case.remaining_budget,
            status=status,
        )
        report_url = report_summary["report_url"]
    except Exception:
        report_url = None
        report_summary = None

    return jsonify({
        "success": is_correct,
        "solved": is_correct,
        "case_id": case.case_id,
        "accused": suspect,
        "culprit": case.culprit if is_correct else None,
        "message": message,
        "reputation": player.reputation,
        "coins": player.coins,
        "score": player.score,
        "status": status,
        "report_url": report_url,
        "report_summary": report_summary,
    }), 200


@app.route("/reports/<path:filename>", methods=["GET"])
def get_report_image(filename: str):
    """Serves generated Matplotlib report images from data/reports."""
    reports_dir = get_reports_dir()
    return send_from_directory(reports_dir, filename)


@app.route("/case/<case_id>/report", methods=["GET"])
def get_case_report(case_id: str):
    """Generates and returns the visual Matplotlib investigation report for a case."""
    try:
        case = case_manager.get_case(case_id)
    except CaseNotFoundError as e:
        return jsonify({"success": False, "error": "CaseNotFoundError", "message": str(e)}), 404

    clues_found = len(player.get_collected_clues(case.case_id))
    total_clues = len(case.expected_clues)
    recall = clues_found / total_clues if total_clues > 0 else 0.0
    case_score = player.case_scores.get(case.case_id, 0)
    status = player.get_case_status(case.case_id)
    stars = 3 if status == "solved" else (1 if clues_found > 0 else 0)

    out_file, summary = generate_case_report_chart(
        case_id=case.case_id,
        case_title=case.title,
        score=case_score,
        stars=stars,
        precision=1.0 if clues_found > 0 else 0.0,
        recall=recall,
        correct_count=clues_found,
        false_count=0,
        searches_used=case.searches_used,
        remaining_budget=case.remaining_budget,
        status=status,
    )

    summary["success"] = True
    return jsonify(summary), 200


# ==============================================================================
# STEP 7: SESSION SAVES (PICKLE), LEADERBOARD (CSV), & NOTES
# ==============================================================================

@app.route("/session/save", methods=["POST"])
def session_save():
    """Saves player session to a local pickle file."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    slot: str = data.get("slot", "detective_save")

    saved_path = save_player_pickle(player_obj=player, slot_name=slot)
    return jsonify({
        "success": True,
        "message": f"Player session saved to slot '{slot}'.",
        "file": saved_path.name,
        "player": player.to_dict(),
    }), 200


@app.route("/session/load", methods=["POST"])
def session_load():
    """Restores player session from a local pickle file."""
    global player
    data: Dict[str, Any] = request.get_json(silent=True) or {}
    slot: str = data.get("slot", "detective_save")

    loaded_player = load_player_pickle(slot_name=slot)
    if loaded_player is None:
        return jsonify({
            "success": False,
            "error": "SaveFileNotFound",
            "message": f"No valid save file found in slot '{slot}'.",
        }), 404

    # Update global player in-place
    player.name = loaded_player.name
    player.reputation = loaded_player.reputation
    player.coins = getattr(loaded_player, "coins", 50)
    player.score = loaded_player.score
    player.collected_clues = loaded_player.collected_clues
    player.solved_cases = loaded_player.solved_cases
    player.failed_cases = loaded_player.failed_cases
    player.case_scores = loaded_player.case_scores

    return jsonify({
        "success": True,
        "message": f"Player session restored from slot '{slot}'.",
        "player": player.to_dict(),
    }), 200


@app.route("/session/saves", methods=["GET"])
def session_list():
    """Returns all available pickle save files."""
    slots = list_save_slots()
    return jsonify({
        "success": True,
        "count": len(slots),
        "saves": slots,
    }), 200


@app.route("/leaderboard", methods=["GET"])
def leaderboard_route():
    """Returns top scores from the CSV leaderboard."""
    entries = get_leaderboard(limit=50)
    return jsonify({
        "success": True,
        "count": len(entries),
        "leaderboard": entries,
    }), 200


@app.route("/notes", methods=["GET", "POST"])
def notes_route():
    """Handles adding and fetching append-only detective notes."""
    if request.method == "POST":
        data: Dict[str, Any] = request.get_json(silent=True) or {}
        note_text: str = data.get("note", "").strip()
        case_id: str = data.get("case_id", "case_01")
        author: str = data.get("author", player.name)

        if not note_text:
            return jsonify({
                "success": False,
                "error": "EmptyNoteError",
                "message": "Field note cannot be empty.",
            }), 400

        entry = append_detective_note(note=note_text, case_id=case_id, author=author)
        return jsonify({
            "success": True,
            "message": "Note recorded in detective journal.",
            "note": entry,
            "all_notes": get_detective_notes(case_id=case_id),
        }), 200
    else:
        case_id = request.args.get("case_id")
        notes = get_detective_notes(case_id=case_id)
        return jsonify({
            "success": True,
            "case_id": case_id,
            "count": len(notes),
            "notes": notes,
        }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "NotFound",
        "message": "The requested resource was not found on the server.",
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": "InternalServerError",
        "message": "An internal server error occurred.",
    }), 500


if __name__ == "__main__":
    app.run(debug=True)
