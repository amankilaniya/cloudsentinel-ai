"""Decision options for the CloudSentinel AI security agent."""

DECISION_OPTIONS = [
    "inspect_iam",
    "inspect_ec2",
    "review_cloudtrail",
    "human_review",
]

DECISION_QUESTION = """
Given a security finding and the evidence collected so far,
choose the most useful next investigation action.
Choose human_review if the evidence is insufficient or ambiguous.
"""
