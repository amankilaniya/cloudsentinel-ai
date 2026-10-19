"""Dispatch CloudSentinel AI investigations to approved tools."""

from typing import Any

from tools.inspect_iam import inspect_iam
from tools.inspect_ec2 import inspect_ec2
from tools.review_cloudtrail import review_cloudtrail


TOOL_HANDLERS = {
    "inspect_iam": inspect_iam,
    "inspect_ec2": inspect_ec2,
    "review_cloudtrail": review_cloudtrail,
}


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
    from agent.decision_request import build_decision_request
    from agent.decider_client import select_action

    if not isinstance(event, dict) or not event:
        return {
            "status": "human_review_required",
            "selected_tool": "human_review",
            "reason": "Missing event data.",
            "result": None,
        }

    try:
        decision = build_decision_request(finding, evidence)
        selection = select_action(decision["state"])
        action = (
            selection.get("selected_tool")
            if isinstance(selection, dict)
            else selection
        )
    except (AttributeError, TypeError, ValueError):
        action = "human_review"

    if action not in TOOL_HANDLERS:
        return {
            "status": "human_review_required",
            "selected_tool": "human_review",
            "reason": "Decider unavailable or human review selected.",
            "result": None,
        }

    return investigate(action, event)
