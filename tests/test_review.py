import unittest
import sys
import os
import json
import tempfile
import io

test_file_path = os.path.abspath(__file__)
repo_root = os.path.dirname(os.path.dirname(test_file_path))

if repo_root not in sys.path:
    sys.path.append(repo_root)

from scripts.review import check_task
from scripts import tasks
from scripts.lib import io as scripts_io

class TestReview(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name
        self.docs_dir = os.path.join(self.repo_root, "docs", "tasks")

        # Monkey patch global variables in tasks module
        self.original_repo_root = tasks.REPO_ROOT
        self.original_docs_dir = tasks.DOCS_DIR
        tasks.REPO_ROOT = self.repo_root
        tasks.DOCS_DIR = self.docs_dir

        os.makedirs(os.path.join(self.docs_dir, "features"), exist_ok=True)

    def tearDown(self):
        tasks.REPO_ROOT = self.original_repo_root
        tasks.DOCS_DIR = self.original_docs_dir
        self.test_dir.cleanup()

    def test_check_task_not_found(self):
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            result = check_task("NONEXISTENT-123", output_format="text")
            self.assertFalse(result)
            self.assertIn("Error: Task ID NONEXISTENT-123 not found.", captured_output.getvalue())
        finally:
            sys.stdout = sys.__stdout__

    def test_check_task_success(self):
        # Create a mock task
        task_id = "FEATURES-123"
        task_content = "---\nid: FEATURES-123\nstatus: in_progress\n---\n# Feature 123\nSome normal text here."
        task_path = os.path.join(self.docs_dir, "features", f"{task_id}.md")
        scripts_io.write_atomic(task_path, task_content)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            result = check_task(task_id, mock_failure=False, output_format="text")
            self.assertTrue(result)
            self.assertIn("Success: No critical issues found for FEATURES-123.", captured_output.getvalue())
        finally:
            sys.stdout = sys.__stdout__

    def test_check_task_mock_failure(self):
        # Create a mock task
        task_id = "FEATURES-123"
        task_content = "---\nid: FEATURES-123\nstatus: in_progress\n---\n# Feature 123\nSome normal text here."
        task_path = os.path.join(self.docs_dir, "features", f"{task_id}.md")
        scripts_io.write_atomic(task_path, task_content)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            result = check_task(task_id, mock_failure=True, output_format="text")
            self.assertFalse(result)
            self.assertIn("Critical Issue: The implementation of FEATURES-123 does not match the spec.", captured_output.getvalue())
        finally:
            sys.stdout = sys.__stdout__

    def test_check_task_critical_issue_in_content(self):
        # Create a mock task with CRITICAL_ISSUE in the text
        task_id = "FEATURES-123"
        task_content = "---\nid: FEATURES-123\nstatus: in_progress\n---\n# Feature 123\nHere is a CRITICAL_ISSUE that needs addressing."
        task_path = os.path.join(self.docs_dir, "features", f"{task_id}.md")
        scripts_io.write_atomic(task_path, task_content)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            result = check_task(task_id, mock_failure=False, output_format="text")
            self.assertFalse(result)
            self.assertIn("Critical Issue: The implementation of FEATURES-123 does not match the spec.", captured_output.getvalue())
        finally:
            sys.stdout = sys.__stdout__

if __name__ == '__main__':
    unittest.main()
