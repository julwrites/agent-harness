import unittest
import os
import sys
import tempfile
import json
from io import StringIO
from unittest.mock import patch

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
import tasks

class TestTaskDependencies(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name
        self.docs_dir = os.path.join(self.repo_root, "docs", "tasks")

        # Monkey patch global variables in tasks module
        self.original_repo_root = tasks.REPO_ROOT
        self.original_docs_dir = tasks.DOCS_DIR

        tasks.REPO_ROOT = self.repo_root
        tasks.DOCS_DIR = self.docs_dir

        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()

        # Init docs structure
        tasks.init_docs()

    def tearDown(self):
        tasks.REPO_ROOT = self.original_repo_root
        tasks.DOCS_DIR = self.original_docs_dir
        self.test_dir.cleanup()
        sys.stdout = self.held

    def create_task_get_id(self, title, dependencies=None):
        sys.stdout = StringIO()
        tasks.create_task("foundation", title, "Desc", dependencies=dependencies, output_format="json")
        output = sys.stdout.getvalue()
        try:
            return json.loads(output)["id"]
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {output}", file=sys.stderr)
            return None

    def test_cannot_start_task_with_pending_dependency(self):
        # Create Task A
        id_a = self.create_task_get_id("Task A")

        # Create Task B depending on A
        id_b = self.create_task_get_id("Task B", dependencies=[id_a])

        # Try to update Task B to in_progress
        # This should fail because Task A is pending
        sys.stdout = StringIO()
        with self.assertRaises(SystemExit) as cm:
            tasks.update_task_status(id_b, "in_progress", output_format="json")

        # Verify error message (optional, but good)
        # self.assertEqual(cm.exception.code, 1) # SystemExit(1)
        # output = json.loads(sys.stdout.getvalue())
        # self.assertIn("error", output)

    def test_can_start_task_with_completed_dependency(self):
        # Create Task A
        id_a = self.create_task_get_id("Task A")

        # Complete Task A
        sys.stdout = StringIO()
        tasks.update_task_status(id_a, "completed", output_format="json")

        # Create Task B depending on A
        id_b = self.create_task_get_id("Task B", dependencies=[id_a])

        # Try to update Task B to in_progress
        # This should succeed
        sys.stdout = StringIO()
        tasks.update_task_status(id_b, "in_progress", output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertTrue(output["success"])
        self.assertEqual(output["status"], "in_progress")

if __name__ == "__main__":
    unittest.main()
