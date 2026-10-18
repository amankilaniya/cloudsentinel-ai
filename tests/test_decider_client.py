import json
import os
import unittest
from unittest.mock import patch

from agent.decider_client import select_action


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class TestDeciderClient(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_endpoint_falls_back_to_human(self):
        self.assertEqual(select_action("finding"), "human_review")

    @patch("agent.decider_client.urlopen")
    @patch.dict(os.environ, {"DECIDER_URL": "http://localhost:8000"})
    def test_valid_choice_is_returned(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({
            "answers": {
                "next_action": {
                    "type": "choice",
                    "choice": "inspect_iam",
                    "confidence": 0.9,
                }
            }
        })

        self.assertEqual(select_action("IAM policy changed"), "inspect_iam")

        request = mock_urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(body["questions"]["next_action"]["type"], "choice")

    @patch("agent.decider_client.urlopen")
    @patch.dict(os.environ, {"DECIDER_URL": "http://localhost:8000"})
    def test_invalid_choice_falls_back_to_human(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse({
            "answers": {
                "next_action": {
                    "type": "choice",
                    "choice": "delete_everything",
                }
            }
        })

        self.assertEqual(select_action("finding"), "human_review")

    @patch("agent.decider_client.urlopen", side_effect=OSError("offline"))
    @patch.dict(os.environ, {"DECIDER_URL": "http://localhost:8000"})
    def test_service_error_falls_back_to_human(self, mock_urlopen):
        self.assertEqual(select_action("finding"), "human_review")


if __name__ == "__main__":
    unittest.main()
