import json
from agent.workflow import investigate

cases = {
    "inspect_iam": {
        "event_name": "AttachUserPolicy",
        "principal": "demo-user",
        "changes": ["AdministratorAccess"],
    },
    "inspect_ec2": {
        "instance_id": "i-demo123456789",
        "public_ip": "203.0.113.10",
        "ssh_open_to_world": True,
        "state": "running",
    },
    "review_cloudtrail": {
        "event_name": "StopLogging",
        "principal": "demo-user",
    },
}

for action, event in cases.items():
    print(f"\n{'=' * 55}")
    print(f"Investigation: {action}")
    print("=" * 55)
    result = investigate(action, event)
    print(json.dumps(result, indent=2))
