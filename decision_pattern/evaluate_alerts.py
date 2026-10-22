"""Run Decider on sample alerts; measure accuracy, confidence and latency.

Run from the project root:   python decision_pattern/evaluate_alerts.py
Optional: only the first N alerts:  python decision_pattern/evaluate_alerts.py 2
Needs the Decider server running. One alert takes about a minute on a CPU.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.decider_client import select_investigation_action

# (finding, evidence, expected tool): expected tools are my first guess,
# please review them with your team.
ALERTS = [
    ("A new access key was created for IAM user alice",
     ["User alice has had no activity for 90 days"], "inspect_iam"),
    ("An IAM role was updated to trust an unknown external account",
     ["Trust policy changed 10 minutes ago"], "inspect_iam"),
    ("Administrator policy attached to a developer user",
     ["User dev-bob now has full permissions"], "inspect_iam"),
    ("Security group opened SSH port 22 to the whole internet",
     ["Instance i-0abc123 is in the affected group"], "inspect_ec2"),
    ("EC2 instance launched with a public IP in an unused region",
     ["Instance type is a large GPU server"], "inspect_ec2"),
    ("Instance i-0def456 has unexpected inbound traffic on port 3389",
     ["The instance is a Windows server"], "inspect_ec2"),
    ("Many failed console login attempts from a new IP address",
     ["14 failures in 5 minutes"], "review_cloudtrail"),
    ("Unusual API calls at 3 AM from an unfamiliar country",
     ["No known user matches this activity"], "review_cloudtrail"),
    ("Audit logging was stopped in the account",
     ["A StopLogging call was recorded"], "review_cloudtrail"),
    ("Something looks odd in the account", [], "human_review"),
    ("Alert received with no details", [], "human_review"),
    ("Unusual cost increase this month",
     ["No resource or user is named"], "human_review"),
]

limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(ALERTS)
rows = []
out_file = Path(__file__).with_name("eval_results.jsonl")

with open(out_file, "w") as f:
    for finding, evidence, expected in ALERTS[:limit]:
        r = select_investigation_action(finding, evidence)  # one at a time
        row = {
            "finding": finding, "expected": expected,
            "model_choice": r["model_choice"], "confidence": r["confidence"],
            "probabilities": r["probabilities"], "latency_ms": r["latency_ms"],
            "reason": r["reason"],
        }
        rows.append(row)
        f.write(json.dumps(row) + "\n")
        ok = "OK " if row["model_choice"] == expected else "BAD"
        print(f"{ok} expected={expected:18} got={row['model_choice']} "
              f"conf={row['confidence']} latency={row['latency_ms']} ms", flush=True)

valid = [r for r in rows if r["model_choice"] is not None]
correct = sum(r["model_choice"] == r["expected"] for r in valid)
print(f"\nAccuracy: {correct}/{len(rows)} (errors: {len(rows) - len(valid)})")
for t in (0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 0.9):
    auto = [r for r in valid if r["confidence"] is not None and r["confidence"] >= t]
    good = sum(r["model_choice"] == r["expected"] for r in auto)
    print(f"threshold {t}: {len(auto)} run automatically, {good} of them correct")