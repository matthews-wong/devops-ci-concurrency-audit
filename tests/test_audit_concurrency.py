import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import audit_concurrency  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class AuditWorkflowTest(unittest.TestCase):
    def test_ref_scoped_cancelling_group_is_clean(self):
        self.assertEqual(audit_concurrency.audit_workflow(FIXTURES / "good.yml"), [])

    def test_pull_request_workflow_without_concurrency_is_flagged(self):
        findings = audit_concurrency.audit_workflow(FIXTURES / "none.yml")
        self.assertEqual(len(findings), 1)
        self.assertIn("sets no concurrency", findings[0])

    def test_group_without_an_expression_is_flagged(self):
        findings = audit_concurrency.audit_workflow(FIXTURES / "static-group.yml")
        self.assertEqual(len(findings), 1)
        self.assertIn("group 'ci' is not scoped to a ref", findings[0])

    def test_job_level_group_without_cancel_is_flagged(self):
        findings = audit_concurrency.audit_workflow(FIXTURES / "no-cancel.yml")
        self.assertEqual(len(findings), 1)
        self.assertIn("job 'test' concurrency does not set cancel-in-progress", findings[0])

    def test_push_only_workflow_is_out_of_scope(self):
        self.assertEqual(audit_concurrency.audit_workflow(FIXTURES / "push-only.yml"), [])

    def test_unreadable_path_is_a_finding_not_a_crash(self):
        findings = audit_concurrency.audit_workflow(FIXTURES / "nope.yml")
        self.assertIn("nope.yml: cannot read", findings[0])


class MainTest(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual(audit_concurrency.main([str(FIXTURES / "good.yml")]), 0)
        self.assertEqual(audit_concurrency.main([str(FIXTURES / "none.yml")]), 1)


if __name__ == "__main__":
    unittest.main()
