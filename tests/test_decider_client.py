import unittest
from unittest.mock import Mock, patch

import requests

from agent.decider_client import select_investigation_action


class TestDeciderClient(unittest.TestCase):
    @patch("agent.decider_client.requests.post")
    def test_accepts_valid_decider_choice(self, post):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "model": "demo-decider",
            "answers": {
                "next_action": {
                    "type": "choice",
                    "choice": "inspect_iam",
                    "confidence": 0.91,
                }
            },
        }
        post.return_value = response

        result = select_investigation_action("Unusual IAM change")

        self.assertEqual(result["selected_tool"], "inspect_iam")
        self.assertEqual(result["status"], "selected")

    @patch("agent.decider_client.requests.post")
    def test_falls_back_when_service_is_unavailable(self, post):
        post.side_effect = requests.ConnectionError("service unavailable")

        result = select_investigation_action("Unusual IAM change")

        self.assertEqual(result["selected_tool"], "human_review")
        self.assertEqual(result["status"], "human_review_required")

    def test_rejects_empty_finding(self):
        with self.assertRaises(ValueError):
            select_investigation_action("  ")


if __name__ == "__main__":
    unittest.main()
