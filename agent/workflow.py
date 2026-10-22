"""Dispatch CloudSentinel AI investigations to approved tools."""

import json
import os
from datetime import datetime, timezone
from typing import Any

from tools.inspect_iam import inspect_iam
from tools.inspect_ec2 import inspect_ec2
from tools.review_cloudtrail import review_cloudtrail


TOOL_HANDLERS = {
    "inspect_iam": inspect_iam,
    "inspect_ec2": inspect_ec2,
    "review_cloudtrail": review_cloudtrail,
}

# Every Decider decision is appended to this file (one JSON object per line).
DECISION_LOG_PATH = os.getenv("DECISION_LOG_PATH", "decisions.jsonl")


def log_decision(finding: str, selection: dict[str, Any]) -> None:
    """Record the selected tool, confidence and latency of one decision."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "finding": str(finding)[:200],  # shortened on purpose
        "selected_tool": selection.get("selected_tool"),
        "model_choice": selection.get("model_choice"),
        "confidence": selection.get("confidence"),
        "probabilities": selection.get("probabilities"),
        "latency_ms": selection.get("latency_ms"),
        "reason": selection.get("reason"),
        "status": selection.get("status"),
    }
    try:
        with open(DECISION_LOG_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(record) + "\n")
    except OSError:
        pass  # a logging problem must never stop an investigation


def investigate(
    action: str,
    event: dict[str, Any] | None,
) -> dict[str, Any]:
    """Run an approved tool or request human review."""
    if action not in TOOL_HANDLERS or not isinstance(event, dict) or not event:
        return {
            "status": "human_review_required",
            "selected_tool": "human_review",
            "reason": "Unknown action or missing event data.",
            "result": None,
        }

    result = TOOL_HANDLERS[action](event)

    return {
        "status": "completed",
        "selected_tool": action,
        "result": result,
    }


def investigate_with_decider(
    finding: str,
    event: dict[str, Any] | None,
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    """Select an action with Decider, then run the approved tool."""
    from agent.decider_client import select_action

    if not isinstance(event, dict) or not event:
        return {
            "status": "human_review_required",
            "selected_tool": "human_review",
            "reason": "Missing event data.",
            "result": None,
            "decision": None,
        }

    try:
        # finding and evidence are passed separately; select_action
        # builds the question text itself.
        selection = select_action(finding, evidence)
    except (AttributeError, TypeError, ValueError):
        selection = None

    if isinstance(selection, dict):
        action = selection.get("selected_tool")
        decision = selection
        # Real Decider results always carry latency_ms; this keeps
        # mocked test data out of the log.
        if "latency_ms" in selection:
            log_decision(finding, selection)
    else:
        action = selection
        decision = None

    if action not in TOOL_HANDLERS:
        return {
            "status": "human_review_required",
            "selected_tool": "human_review",
            "reason": "Decider unavailable or human review selected.",
            "result": None,
            "decision": decision,
        }

    result = investigate(action, event)
    result["decision"] = decision
    return result