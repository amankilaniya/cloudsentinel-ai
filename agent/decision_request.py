"""Build structured investigation requests for CloudSentinel AI."""

from agent.decision_options import DECISION_OPTIONS, DECISION_QUESTION


def build_decision_request(
    finding: str,
    evidence: list[str] | None = None,
) -> dict:
    """Build a request for selecting the next investigation action."""
    finding = finding.strip()

    if not finding:
        raise ValueError("Finding must not be empty.")

    return {
        "state": (
            f"{DECISION_QUESTION.strip()}\n\n"
            f"Security finding: {finding}\n"
            f"Evidence collected: {evidence or []}"
        ),
        "question": "Which investigation action should be taken next?",
        "options": DECISION_OPTIONS.copy(),
    }
