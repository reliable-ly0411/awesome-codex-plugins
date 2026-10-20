"""Regression tests for the centralized catalog gate and contributor comments."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import yaml


SCRIPTS = Path(__file__).parent
SPEC = importlib.util.spec_from_file_location(
    "awesome_codex_centralized_publisher",
    SCRIPTS / "publish-open-pr-checks-centralized.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load centralized publisher")
PUBLISHER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PUBLISHER
SPEC.loader.exec_module(PUBLISHER)


class CentralizedPublisherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scan_result = {
            "pr_number": 12,
            "head_sha": "a" * 40,
            "title": "Example plugin",
            "author_login": "contributor",
            "state": "scan",
            "failure_reasons": [],
            "contributions": [{"owner": "example", "repo": "plugin"}],
        }

    def test_completed_scan_meeting_score_and_severity_gates_passes(self) -> None:
        conclusion, title, summary = PUBLISHER.check_summary(
            self.scan_result, {12: ["success"]}
        )
        self.assertEqual(conclusion, "success")
        self.assertIn("thresholds passed", title)
        self.assertIn("no critical/high findings", summary)

    def test_missing_or_failed_scan_does_not_pass(self) -> None:
        for jobs in ({}, {12: ["failure"]}, {12: ["success", "failure"]}):
            with self.subTest(jobs=jobs):
                conclusion, title, summary = PUBLISHER.check_summary(self.scan_result, jobs)
                self.assertEqual(conclusion, "failure")
                self.assertIn("scan gates not established", title.lower())
                self.assertIn("at least 80/100", summary)

    def test_scan_comments_are_single_paragraphs_and_recommend_optional_source_ci(self) -> None:
        for jobs in ({12: ["success"]}, {12: ["failure"]}):
            conclusion, title, summary = PUBLISHER.check_summary(self.scan_result, jobs)
            comment = PUBLISHER.remediation_comment(
                self.scan_result, conclusion, title, summary, "https://example.test/run"
            )
            self.assertNotIn("\n", comment)
            self.assertNotIn("\\n", comment)
            if conclusion == "failure":
                self.assertIn("recommended, not required", comment)
                self.assertIn("score is below 80", comment)
                self.assertIn("source repository does not already run the scanner", comment)

    def test_no_new_entry_success_comment_does_not_claim_a_score(self) -> None:
        result = {**self.scan_result, "state": "success"}
        comment = PUBLISHER.remediation_comment(
            result,
            "success",
            "Contribution requirements passed",
            "No new Community Plugins entries require validation.",
            "https://example.test/run",
        )
        self.assertNotIn("\n", comment)
        self.assertIn("No new Community Plugins entries", comment)
        self.assertNotIn("score threshold", comment)

    def test_catalog_failure_comment_is_single_paragraph(self) -> None:
        result = {
            **self.scan_result,
            "state": "failure",
            "failure_reasons": ["README entry is not alphabetical", "Missing repository metadata"],
        }
        comment = PUBLISHER.remediation_comment(
            result,
            "failure",
            "Catalog validation failed",
            "Catalog validation failed: README entry is not alphabetical",
            "https://example.test/run",
        )
        self.assertNotIn("\n", comment)
        self.assertNotIn("\\n", comment)
        self.assertIn("README entry is not alphabetical", comment)

    def test_base_publisher_keeps_scanner_failure_separate_from_catalog_failure(self) -> None:
        base = PUBLISHER.PUBLISHER
        conclusion, title, summary = base.check_summary(self.scan_result, {12: ["failure"]})
        self.assertEqual(conclusion, "failure")
        self.assertIn("Centralized scan gates not established", title)
        self.assertNotIn("Required scanner CI is missing", summary)
        comment = base.remediation_comment(
            self.scan_result, conclusion, title, summary, "https://example.test/run"
        )
        self.assertNotIn("\n", comment)
        self.assertIn("Source-repository scanner CI is optional", comment)
        self.assertIn("source repository does not already run the scanner", comment)


class ScannerPolicyTests(unittest.TestCase):
    def test_catalog_workflows_preserve_severity_and_score_gates(self) -> None:
        workflows = SCRIPTS.parent / ".github" / "workflows"
        for filename in (
            "scanner-example.yml",
            "scanner-example-lint.yml",
            "validate-contribution.yml",
            "sweep-open-prs.yml",
        ):
            with self.subTest(workflow=filename):
                document = yaml.safe_load((workflows / filename).read_text())
                scanner_steps = [
                    step
                    for job in document["jobs"].values()
                    for step in job.get("steps", [])
                    if step.get("uses", "").startswith(
                        "hashgraph-online/ai-plugin-scanner-action@"
                    )
                ]
                self.assertTrue(scanner_steps)
                for step in scanner_steps:
                    self.assertEqual(step["with"]["fail_on_severity"], "high")
                    if step["with"]["mode"] == "scan":
                        self.assertEqual(step["with"]["min_score"], 80)
                for job in document["jobs"].values():
                    self.assertFalse(job.get("continue-on-error", False))

    def test_strict_example_keeps_its_stronger_thresholds(self) -> None:
        path = SCRIPTS.parent / ".github/workflows/scanner-example-strict.yml"
        document = yaml.safe_load(path.read_text())
        step = document["jobs"]["scan"]["steps"][1]
        self.assertEqual(step["with"]["min_score"], 90)
        self.assertEqual(step["with"]["fail_on_severity"], "medium")


if __name__ == "__main__":
    unittest.main()
