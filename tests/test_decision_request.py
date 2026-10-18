import unittest

from agent.decision_options import DECISION_OPTIONS
from agent.decision_request import build_decision_request


class TestDecisionRequest(unittest.TestCase):
    def test_builds_request(self):
        request = build_decision_request(
            "Unusual IAM permission change",
            ["An IAM policy was modified"],
        )
        self.assertIn("Unusual IAM permission change", request["state"])
        self.assertEqual(request["options"], DECISION_OPTIONS)

    def test_evidence_can_be_omitted(self):
        request = build_decision_request("Suspicious EC2 activity")
        self.assertIn("[]", request["state"])

    def test_empty_finding_is_rejected(self):
        with self.assertRaises(ValueError):
            build_decision_request("   ")


if __name__ == "__main__":
    unittest.main()
