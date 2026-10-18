import json
import unittest
from pathlib import Path

from tools.inspect_ec2 import inspect_ec2


class TestInspectEC2(unittest.TestCase):
    def test_detects_public_ssh_exposure(self):
        event = json.loads(
            Path("sample-data/ec2_event.json").read_text()
        )
        result = inspect_ec2(event)

        self.assertEqual(result["tool"], "inspect_ec2")
        self.assertEqual(result["risk_level"], "high")
        self.assertIn(
            "SSH access is open to the internet",
            result["findings"],
        )


if __name__ == "__main__":
    unittest.main()
