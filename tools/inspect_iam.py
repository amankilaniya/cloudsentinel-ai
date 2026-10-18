"""Inspect sample IAM security events for CloudSentinel AI."""

from typing import Any


def inspect_iam(event: dict[str, Any]) -> dict[str, Any]:
    """Return evidence from a sample IAM event."""
    event_name = event.get("event_name", "Unknown")
    principal = event.get("principal", "Unknown")
    changes = event.get("changes", [])

    suspicious_events = {
        "CreateAccessKey",
        "AttachUserPolicy",
        "PutUserPolicy",
        "CreateLoginProfile",
    }

    is_suspicious = event_name in suspicious_events

    return {
        "tool": "inspect_iam",
        "event_name": event_name,
        "principal": principal,
        "suspicious": is_suspicious,
        "risk_level": "high" if is_suspicious else "undetermined",
        "evidence": changes,
        "recommendation": (
            "Review the IAM change and verify whether it was authorized."
            if is_suspicious
            else "Collect more context before assessing this event."
        ),
    }
