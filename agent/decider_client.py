"""HTTP client for the Strands Decider System One API."""

import os
import time  # NEW: to measure how long Decider takes
from typing import Any

import requests

from agent.decision_options import DECISION_OPTIONS, DECISION_QUESTION


DEFAULT_DECIDER_URL = "http://127.0.0.1:8000"

# NEW: below this confidence, we do not trust Decider and ask a human.
# 0.9 is only a starting value; we tune it after testing real alerts.
MIN_CONFIDENCE = float(os.getenv("DECIDER_MIN_CONFIDENCE", "0.9"))


def select_investigation_action(
    finding: str,
    evidence: list[str] | None = None,
    timeout: float = 5.0,
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
                "criteria": {
                    option: option.replace("_", " ")
                    for option in [*DECISION_OPTIONS]
                },
            }
        },
    }

    started = time.perf_counter()  # NEW: start the stopwatch

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

        latency_ms = round((time.perf_counter() - started) * 1000, 1)  # NEW
        confidence = answer.get("confidence")

        # NEW: low confidence -> do not trust the choice, ask a human
        if confidence is None or confidence < MIN_CONFIDENCE:
            return {
                "selected_tool": "human_review",
                "model_choice": action,  # what Decider wanted, kept for the log
                "confidence": confidence,
                "model": data.get("model"),
                "status": "human_review_required",
                "reason": "low_confidence",
                "latency_ms": latency_ms,
            }

        return {
            "selected_tool": action,
            "model_choice": action,  # NEW
            "confidence": confidence,
            "model": data.get("model"),
            "status": "selected",
            "reason": "decider_choice",  # NEW
            "latency_ms": latency_ms,  # NEW
        }

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return {
            "selected_tool": "human_review",
            "model_choice": None,  # NEW
            "confidence": None,
            "model": None,
            "status": "human_review_required",
            "reason": "service_error",  # NEW
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),  # NEW
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