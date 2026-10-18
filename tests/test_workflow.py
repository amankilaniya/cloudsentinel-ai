from unittest.mock import patch
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


class TestDeciderWorkflow(unittest.TestCase):
    @patch("agent.decider_client.select_action", return_value="inspect_iam")
    def test_model_choice_dispatches_iam_tool(self, mock_select):
        from agent.workflow import investigate_with_decider

        result = investigate_with_decider(
            finding="An IAM policy changed",
            event={"eventName": "AttachUserPolicy"},
        )

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["selected_tool"], "inspect_iam")
        mock_select.assert_called_once()

    @patch("agent.decider_client.select_action", return_value="human_review")
    def test_human_review_choice_does_not_run_tool(self, mock_select):
        from agent.workflow import investigate_with_decider

        result = investigate_with_decider(
            finding="Ambiguous security finding",
            event={"eventName": "UnknownEvent"},
        )

        self.assertEqual(result["status"], "human_review_required")
        self.assertEqual(result["selected_tool"], "human_review")
        self.assertIsNone(result["result"])
