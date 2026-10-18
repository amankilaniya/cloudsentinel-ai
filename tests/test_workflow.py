import unittest

from agent.workflow import investigate


class TestWorkflow(unittest.TestCase):
    def test_dispatches_iam_tool(self):
        result = investigate(
            "inspect_iam",
            {
                "event_name": "AttachUserPolicy",
                "principal": "demo-user",
                "changes": ["Policy attached"],
            },
        )
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_tool"], "inspect_iam")

    def test_unknown_action_requires_human_review(self):
        result = investigate("unknown_tool", {"event_name": "Unknown"})
        self.assertEqual(result["selected_tool"], "human_review")
        self.assertEqual(result["status"], "human_review_required")

    def test_missing_event_requires_human_review(self):
        result = investigate("inspect_ec2", None)
        self.assertEqual(result["selected_tool"], "human_review")


if __name__ == "__main__":
    unittest.main()
