"""HTTP client for the Strands Decider System One API."""

import os
from typing import Any

import requests

from agent.decision_options import DECISION_OPTIONS, DECISION_QUESTION


DEFAULT_DECIDER_URL = "http://127.0.0.1:8000"


def select_investigation_action(
    finding: str,
    evidence: list[str] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Ask Decider to select an investigation action.

    Returns human_review when the service is unavailable or its answer
    cannot be validated.
    """
    finding = finding.strip()
    if not finding:
        raise ValueError("Finding must not be empty.")

    base_url = os.getenv("DECIDER_BASE_URL", DEFAULT_DECIDER_URL).rstrip("/")
    state = (
        f"{DECISION_QUESTION.strip()}\n\n"
        f"Security finding: {finding}\n"
        f"Evidence collected: {evidence or []}"
    )

    payload = {
        "state": state,
        "model": "strands-decider-latest",
        "questions": {
            "next_action": {
                "type": "choice",
                "instructions": (
                    "Choose the most useful next investigation action. "
                    "Choose human_review if evidence is insufficient."
                ),
                "criteria": {
                    option: option.replace("_", " ")
                    for option in [*DECISION_OPTIONS]
                },
            }
        },
    }

    try:
        response = requests.post(
            f"{base_url}/v1/systemone",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        answer = data["answers"]["next_action"]
        action = answer["choice"]

        if action not in DECISION_OPTIONS:
            raise ValueError("Decider returned an unsupported action.")

        return {
            "selected_tool": action,
            "confidence": answer.get("confidence"),
            "model": data.get("model"),
            "status": "selected",
        }

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return {
            "selected_tool": "human_review",
            "confidence": None,
            "model": None,
            "status": "human_review_required",
        }


def select_action(
    finding: str,
    evidence: list[str] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Compatibility wrapper for the workflow's action-selection API."""
    return select_investigation_action(
        finding=finding,
        evidence=evidence,
        timeout=timeout,
    )
