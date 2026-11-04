"""Flask Application for Regex Detective / Shadowfiles."""
from typing import Any, Dict
from flask import Flask, jsonify, request

from game.engine import DetectiveEngine
from game.exceptions import (
    CaseNotFoundError,
    InvalidWarrantError,
    WarrantBudgetExceeded,
)
from game.storage import case_manager, player

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """API landing and system status endpoint."""
    return jsonify({
        "app": "Regex Detective / Shadowfiles",
        "status": "online",
        "message": "Cybercrime Bureau is active. Access /case/<id> to inspect an active case file.",
        "player": player.to_dict(),
        "available_cases": case_manager.list_cases(),
    }), 200


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

    if is_correct:
        player.mark_solved(case.case_id)
        player.reward_reputation(20)
        player.score += 200

        return jsonify({
            "success": True,
            "solved": True,
            "case_id": case.case_id,
            "accused": suspect,
            "culprit": case.culprit,
            "message": f"Case Solved! {case.culprit} has been arrested and confessed.",
            "reputation": player.reputation,
            "score": player.score,
            "status": "solved",
        }), 200
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

        return jsonify({
            "success": False,
            "solved": False,
            "case_id": case.case_id,
            "accused": suspect,
            "message": message,
            "reputation": player.reputation,
            "score": player.score,
            "status": status,
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
