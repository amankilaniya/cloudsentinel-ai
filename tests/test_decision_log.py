import json
import os
import tempfile
import unittest
from unittest.mock import patch

from agent import workflow


class TestDecisionLog(unittest.TestCase):
    def test_decision_is_written_to_the_log(self):
        selection = {
            "selected_tool": "inspect_iam",
            "model_choice": "inspect_iam",
            "confidence": 0.55,
            "probabilities": {"inspect_iam": 0.55},
            "status": "selected",
            "reason": "decider_choice",
            "latency_ms": 123.4,
        }
        with tempfile.TemporaryDirectory() as folder:
            log_path = os.path.join(folder, "decisions.jsonl")
            with patch.object(workflow, "DECISION_LOG_PATH", log_path), patch(
                "agent.decider_client.select_action", return_value=selection
            ):
                result = workflow.investigate_with_decider(
                    finding="IAM policy changed",
                    event={"event_name": "AttachUserPolicy", "principal": "bob"},
                )

            with open(log_path, encoding="utf-8") as log_file:
                lines = log_file.read().strip().splitlines()

        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["selected_tool"], "inspect_iam")
        self.assertEqual(record["confidence"], 0.55)
        self.assertEqual(record["latency_ms"], 123.4)
        self.assertEqual(result["decision"]["confidence"], 0.55)


if __name__ == "__main__":
    unittest.main()