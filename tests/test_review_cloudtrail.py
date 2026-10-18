import json
import unittest
from pathlib import Path

from tools.review_cloudtrail import review_cloudtrail


class TestReviewCloudTrail(unittest.TestCase):
    def test_flags_stop_logging(self):
        event = json.loads(
            Path("sample-data/cloudtrail_event.json").read_text()
        )
        result = review_cloudtrail(event)

        self.assertEqual(result["tool"], "review_cloudtrail")
        self.assertTrue(result["flagged_for_review"])
        self.assertEqual(result["risk_level"], "review")
        self.assertIn("StopLogging", result["evidence"][0])


if __name__ == "__main__":
    unittest.main()
