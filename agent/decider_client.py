"""HTTP client for the Strands Decider typed-choice API."""

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent.decision_options import DECISION_OPTIONS


OPTION_DESCRIPTIONS = {
    "inspect_iam": "Investigate IAM users, roles, access keys, or policy changes.",
    "inspect_ec2": "Investigate EC2 instances, network exposure, or security groups.",
    "review_cloudtrail": "Review CloudTrail activity for suspicious or sensitive actions.",
    "human_review": "Request human review when evidence is insufficient or ambiguous.",
}


def select_action(state: str) -> str:
    """Ask a configured Decider endpoint for the next action.

    Fail closed to human review if the service is unavailable or its
    response is invalid. This function does not execute any investigation tool.
    """
    endpoint = os.getenv("DECIDER_URL", "").strip().rstrip("/")
    model = os.getenv("DECIDER_MODEL", "strands-decider-2b")

    if not endpoint or not state.strip():
        return "human_review"

    payload = {
        "model": model,
        "state": state,
        "questions": {
            "next_action": {
                "type": "choice",
                "instructions": (
                    "Choose the single most useful next cloud-security "
                    "investigation action based on the supplied evidence. "
                    "Choose human_review if the evidence is insufficient "
                    "or ambiguous."
                ),
                "criteria": OPTION_DESCRIPTIONS,
            }
        },
    }

    request = Request(
        f"{endpoint}/v1/systemone",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

        action = result["answers"]["next_action"]["choice"]
        if action in DECISION_OPTIONS:
            return action

    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ):
        pass

    return "human_review"
