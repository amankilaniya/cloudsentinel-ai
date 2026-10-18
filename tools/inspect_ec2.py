"""Inspect sample EC2 security events for CloudSentinel AI."""

from typing import Any


def inspect_ec2(event: dict[str, Any]) -> dict[str, Any]:
    """Summarize EC2 exposure and instance-state evidence."""
    instance_id = event.get("instance_id", "Unknown")
    public_ip = event.get("public_ip")
    security_group_open = event.get("ssh_open_to_world", False)
    state = event.get("state", "unknown")

    findings = []

    if public_ip:
        findings.append("Instance has a public IP address")

    if security_group_open:
        findings.append("SSH access is open to the internet")

    if state == "stopped":
        findings.append("Instance is stopped")

    if security_group_open:
        risk_level = "high"
    elif public_ip:
        risk_level = "review"
    else:
        risk_level = "undetermined"

    return {
        "tool": "inspect_ec2",
        "instance_id": instance_id,
        "state": state,
        "findings": findings,
        "risk_level": risk_level,
        "recommendation": (
            "Review inbound rules and restrict SSH to trusted sources."
            if security_group_open
            else "Review the instance configuration and network exposure."
        ),
    }
