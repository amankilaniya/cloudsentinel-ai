import json
import unittest
from pathlib import Path

from tools.inspect_iam import inspect_iam


class TestInspectIAM(unittest.TestCase):
    def test_detects_sample_policy_change(self):
        path = Path("sample-data/iam_event.json")
        event = json.loads(path.read_text())
        result = inspect_iam(event)

        self.assertEqual(result["tool"], "inspect_iam")
        self.assertTrue(result["suspicious"])
        self.assertEqual(result["risk_level"], "high")
        self.assertEqual(len(result["evidence"]), 2)


if __name__ == "__main__":
    unittest.main()
