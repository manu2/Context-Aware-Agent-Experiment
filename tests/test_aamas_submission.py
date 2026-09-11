import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "aamas_submission_verifier", ROOT / "benchmarks/verify_aamas_submission.py"
)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class AAMASSubmissionVerifierTests(unittest.TestCase):
    def test_draft_sources_are_anonymous_and_official(self):
        self.assertEqual(VERIFIER.source_issues(release=False), [])

    def test_release_mode_rejects_current_placeholders(self):
        issues = VERIFIER.source_issues(release=True)
        self.assertTrue(any("placeholder" in issue for issue in issues))
        self.assertTrue(any("PENDING" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
