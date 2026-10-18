import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.decision_options import DECISION_OPTIONS, DECISION_QUESTION


class TestDecisionOptions(unittest.TestCase):
    def test_options_are_unique(self):
        self.assertEqual(len(DECISION_OPTIONS), len(set(DECISION_OPTIONS)))

    def test_expected_options_exist(self):
        self.assertEqual(
            set(DECISION_OPTIONS),
            {
                "inspect_iam",
                "inspect_ec2",
                "review_cloudtrail",
                "human_review",
            },
        )

    def test_question_is_defined(self):
        self.assertTrue(DECISION_QUESTION.strip())


if __name__ == "__main__":
    unittest.main()
