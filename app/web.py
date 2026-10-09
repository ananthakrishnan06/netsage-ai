"""Local web application for the NetSage diagnosis console."""

import csv
import json
import threading
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from app.ai_engine import VALID_CATEGORIES, run_groq_ai
from app.evaluator import evaluate_case


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "cases_final.csv"
REVIEWS_FILE = ROOT / "data" / "human_reviews.jsonl"
UI_DIR = ROOT / "ui"
_review_lock = threading.Lock()


def _read_cases():
    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def _read_reviews():
    if not REVIEWS_FILE.exists():
        return []
    reviews = []
    with REVIEWS_FILE.open("r", encoding="utf-8") as source:
        for line in source:
            try:
                review = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(review, dict):
                reviews.append(review)
    return reviews


async def index(_request: Request):
    return FileResponse(UI_DIR / "index.html")


async def cases(_request: Request):
    safe_fields = (
        "case_id",
        "issue_type",
        "symptom",
        "topology_note",
        "show_command",
        "show_command_output",
        "severity",
        "verification_command",
        "verification_result",
    )
    items = [
        {field: row.get(field, "") or "" for field in safe_fields}
        for row in _read_cases()
    ]
    return JSONResponse({"cases": items, "model": "Groq"})


async def dashboard(_request: Request):
    records = _read_cases()
    reviews = _read_reviews()
    statuses = {}
    categories = {}
    for row in records:
        status = row.get("evaluation_status") or "Needs Review"
        category = row.get("expected_category") or "OTHER"
        statuses[status] = statuses.get(status, 0) + 1
        categories[category] = categories.get(category, 0) + 1

    correct = statuses.get("Correct", 0)
    corrections = [
        {
            "case_id": row.get("case_id", ""),
            "decision": "Edited",
            "correction": row.get("human_correction", ""),
            "ai_predicted_category": row.get("ai_predicted_category", ""),
            "reason": row.get("correction_reason", ""),
        }
        for row in records
        if row.get("human_decision") == "Edited"
    ]
    corrections.extend(
        review for review in reviews if review.get("decision") == "Edited"
    )
    total = len(records)
    rows = [
        {
            "case_id": row.get("case_id", ""),
            "issue_type": row.get("issue_type", ""),
            "severity": row.get("severity", ""),
            "evaluation_status": row.get("evaluation_status") or "Needs Review",
            "expected_category": row.get("expected_category") or "OTHER",
            "ai_predicted_category": row.get("ai_predicted_category", ""),
        }
        for row in records
    ]
    return JSONResponse(
        {
            "total_cases": total,
            "correct_cases": correct,
            "incorrect_cases": statuses.get("Incorrect", 0),
            "needs_review": statuses.get("Needs Review", 0),
            "accuracy": correct / total if total else 0,
            "human_corrections": len(corrections),
            "category_counts": categories,
            "status_counts": statuses,
            "cases": rows,
            "corrections": corrections,
        }
    )


async def diagnose(request: Request):
    try:
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"error": "Request body must be valid JSON."}, status_code=400)

    if not isinstance(payload, dict):
        return JSONResponse({"error": "Request body must be a JSON object."}, status_code=400)

    case_id = str(payload.get("case_id", "")).strip()
    case = next((row for row in _read_cases() if row.get("case_id") == case_id), None)
    if not case:
        return JSONResponse({"error": "Choose a valid case."}, status_code=404)

    try:
        result = await run_in_threadpool(run_groq_ai, case)
        evaluation = evaluate_case(case, result)
        return JSONResponse(
            {"diagnosis": json.loads(result), "evaluation": evaluation}
        )
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=502)


async def save_review(request: Request):
    try:
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"error": "Request body must be valid JSON."}, status_code=400)

    if not isinstance(payload, dict):
        return JSONResponse({"error": "Request body must be a JSON object."}, status_code=400)

    case_id = str(payload.get("case_id", "")).strip()
    decision = str(payload.get("decision", "")).strip()
    correction = str(payload.get("correction", "")).strip().upper()
    reason = str(payload.get("reason", "")).strip()
    valid_ids = {row.get("case_id") for row in _read_cases()}
    if case_id not in valid_ids:
        return JSONResponse({"error": "Choose a valid case."}, status_code=404)
    if decision not in {"Accepted", "Edited", "Rejected"}:
        return JSONResponse({"error": "Choose a valid review decision."}, status_code=400)
    if decision == "Edited" and correction not in VALID_CATEGORIES:
        return JSONResponse({"error": "Choose a valid correction category."}, status_code=400)

    review = {
        "case_id": case_id,
        "decision": decision,
        "correction": correction if decision == "Edited" else "",
        "reason": reason,
        "ai_predicted_category": str(payload.get("ai_predicted_category", "")),
    }
    with _review_lock:
        REVIEWS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with REVIEWS_FILE.open("a", encoding="utf-8") as destination:
            destination.write(json.dumps(review, ensure_ascii=False) + "\n")
    return JSONResponse({"saved": True, "review": review})


routes = [
    Route("/", index),
    Route("/api/cases", cases),
    Route("/api/dashboard", dashboard),
    Route("/api/diagnose", diagnose, methods=["POST"]),
    Route("/api/reviews", save_review, methods=["POST"]),
    Mount("/static", app=StaticFiles(directory=UI_DIR / "static"), name="static"),
]

app = Starlette(debug=False, routes=routes)
