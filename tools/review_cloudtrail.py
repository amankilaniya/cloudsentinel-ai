"""Review sample CloudTrail events for CloudSentinel AI."""

from typing import Any

SENSITIVE_EVENTS = {
    "ConsoleLogin",
    "StopLogging",
    "DeleteTrail",
    "AuthorizeSecurityGroupIngress",
    "PutBucketPolicy",
}


def review_cloudtrail(event: dict[str, Any]) -> dict[str, Any]:
    """Summarize a CloudTrail event for investigation."""
    event_name = event.get("event_name", "Unknown")
    principal = event.get("principal", "Unknown")
    event_time = event.get("event_time", "Unknown")
    source_ip = event.get("source_ip", "Unknown")
    error_code = event.get("error_code")

    flagged = event_name in SENSITIVE_EVENTS

    evidence = [
        f"Event: {event_name}",
        f"Principal: {principal}",
        f"Time: {event_time}",
        f"Source IP: {source_ip}",
    ]

    if error_code:
        evidence.append(f"Error code: {error_code}")

    return {
        "tool": "review_cloudtrail",
        "event_name": event_name,
        "principal": principal,
        "flagged_for_review": flagged,
        "evidence": evidence,
        "risk_level": "review" if flagged else "undetermined",
        "recommendation": (
            "Verify the actor, timing, and authorization for this event."
            if flagged
            else "Correlate with related events before drawing conclusions."
        ),
    }
