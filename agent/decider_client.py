"""HTTP client for the Strands Decider System One API."""

import os
import time
from typing import Any

import requests

from agent.decision_options import DECISION_OPTIONS, DECISION_QUESTION


DEFAULT_DECIDER_URL = "http://127.0.0.1:8000"

# The model is slow on a laptop without a GPU (about 40-55 s per decision),
# so the default wait is long. It can be changed with DECIDER_TIMEOUT.
DEFAULT_TIMEOUT = float(os.getenv("DECIDER_TIMEOUT", "120"))

# Below this confidence we do not trust Decider and ask a human.
MIN_CONFIDENCE = float(os.getenv("DECIDER_MIN_CONFIDENCE", "0.4"))

# The model reads these sentences, so they should be clear.
OPTION_DESCRIPTIONS = {
    "inspect_iam": "Investigate IAM users, roles, access keys, or policy changes.",
    "inspect_ec2": "Investigate EC2 instances, network exposure, or security groups.",
    "review_cloudtrail": "Review CloudTrail activity for suspicious or sensitive actions.",
    "human_review": "Request human review when evidence is insufficient or ambiguous.",
}


def select_investigation_action(
    finding: str,
    evidence: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Ask Decider to select an investigation action.

    Returns human_review when the service is unavailable, its answer
    cannot be validated, or its confidence is too low.
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
                "criteria": OPTION_DESCRIPTIONS,
            }
        },
    }

    started = time.perf_counter()

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

        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        confidence = answer.get("confidence")
        probabilities = answer.get("probabilities")

        if confidence is None or confidence < MIN_CONFIDENCE:
            return {
                "selected_tool": "human_review",
                "model_choice": action,
                "confidence": confidence,
                "probabilities": probabilities,
                "model": data.get("model"),
                "status": "human_review_required",
                "reason": "low_confidence",
                "latency_ms": latency_ms,
            }

        return {
            "selected_tool": action,
            "model_choice": action,
            "confidence": confidence,
            "probabilities": probabilities,
            "model": data.get("model"),
            "status": "selected",
            "reason": "decider_choice",
            "latency_ms": latency_ms,
        }

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return {
            "selected_tool": "human_review",
            "model_choice": None,
            "confidence": None,
            "probabilities": None,
            "model": None,
            "status": "human_review_required",
            "reason": "service_error",
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
        }


def select_action(
    finding: str,
    evidence: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Compatibility wrapper for the workflow's action-selection API."""
    return select_investigation_action(
        finding=finding,
        evidence=evidence,
        timeout=timeout,
    )