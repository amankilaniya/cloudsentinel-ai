import unittest

from backend.app import create_app


class TestCloudSentinelAPI(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "healthy")

    def test_invalid_investigation_request(self):
        response = self.client.post(
            "/api/investigate",
            json={},
        )

        self.assertEqual(response.status_code, 400)

    def test_investigation_endpoint_returns_tool_result(self):
        from unittest.mock import patch

        with patch(
            "agent.decider_client.select_action",
            return_value={"selected_tool": "inspect_iam"},
        ):
            response = self.client.post(
                "/api/investigate",
                json={
                    "finding": "Potentially risky IAM policy change",
                    "event": {
                        "event_name": "AttachUserPolicy",
                        "principal": "demo-user",
                        "changes": ["Policy attached"],
                    },
                    "evidence": ["Synthetic IAM event"],
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "completed")
        self.assertEqual(response.json["selected_tool"], "inspect_iam")
        self.assertEqual(
            response.json["result"]["risk_level"],
            "high",
        )


if __name__ == "__main__":
    unittest.main()
