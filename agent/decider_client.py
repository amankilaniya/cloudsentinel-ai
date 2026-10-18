"""HTTP client for the Strands Decider System One API."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import ValidationError
from strands_decider.schema import SystemOneRequest, SystemOneResponse

from agent.decision_options import DECISION_OPTIONS

OPTION_DESCRIPTIONS = {
    "inspect_iam": "Investigate IAM users, roles, access keys, or policy changes.",
    "inspect_ec2": "Investigate EC2 instances, network exposure, or security groups.",
    "review_cloudtrail": "Review CloudTrail activity for suspicious or sensitive actions.",
    "human_review": "Request human review when evidence is insufficient or ambiguous.",
}

def select_action(state: str) -> str:
    """Ask Decider for an action; default safely to human review."""
    endpoint = os.getenv("DECIDER_URL", "").strip().rstrip("/")
    model = os.getenv("DECIDER_MODEL", "strands-decider-latest")
    if not endpoint or not isinstance(state, str) or not state.strip():
        return "human_review"

    payload = {
        "model": model,
        "state": state,
        "questions": {
            "next_action": {
                "type": "choice",
                "instructions": (
                    "Choose the most useful next cloud-security investigation "
                    "action. Choose human_review if evidence is insufficient "
                    "or ambiguous."
                ),
                "criteria": OPTION_DESCRIPTIONS,
            }
        },
    }

    try:
        validated = SystemOneRequest.model_validate(payload)
        request = Request(
            f"{endpoint}/v1/systemone",
            data=validated.model_dump_json().encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=10) as response:
            raw = json.loads(response.read().decode("utf-8"))

        result = SystemOneResponse.model_validate(raw)
        answer = result.answers.get("next_action")
        if answer is not None and answer.type == "choice":
            if answer.choice in DECISION_OPTIONS:
                return answer.choice
    except (
        HTTPError, URLError, TimeoutError, OSError,
        ValueError, TypeError, KeyError, ValidationError,
    ):
        pass

    return "human_review"
