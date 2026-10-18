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
