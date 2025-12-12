import unittest
import os
import sys
import tempfile
import shutil
import json
from io import StringIO
from unittest.mock import patch

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
import tasks

class TestTasks(unittest.TestCase):
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

    def test_init(self):
        self.assertTrue(os.path.exists(os.path.join(self.docs_dir, "foundation")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_root, "docs", "architecture")))

    def test_create_review_task(self):
        tasks.create_task("review", "Review PR 123", "Checking implementation")
        files = os.listdir(os.path.join(self.docs_dir, "review"))
        task_files = [f for f in files if f.endswith(".md") and f != ".keep"]
        self.assertEqual(len(task_files), 1)
        self.assertTrue(task_files[0].startswith("REVIEW-"))

    def test_create_task(self):
        tasks.create_task("foundation", "My Task", "Description")
        output = sys.stdout.getvalue()
        self.assertIn("Created task:", output)

        # Find the created file
        files = os.listdir(os.path.join(self.docs_dir, "foundation"))
        task_files = [f for f in files if f.endswith(".md") and f != ".keep"]
        self.assertEqual(len(task_files), 1)

        with open(os.path.join(self.docs_dir, "foundation", task_files[0]), "r") as f:
            content = f.read()
            self.assertIn("title: My Task", content)
            self.assertIn("status: pending", content)

    def test_list_tasks(self):
        tasks.create_task("foundation", "Task 1", "Desc")
        tasks.create_task("features", "Task 2", "Desc")

        # Reset stdout
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        output = sys.stdout.getvalue()
        data = json.loads(output)
        self.assertEqual(len(data), 2)

    def test_find_task_moved_file_bug(self):
        # Create a task
        tasks.create_task("foundation", "Moved Task", "Desc")
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_id = data[0]['id']
        filepath = data[0]['filepath']

        # Move it to a subfolder (which optimization might miss)
        new_dir = os.path.join(self.docs_dir, "foundation", "archive")
        os.makedirs(new_dir, exist_ok=True)
        new_path = os.path.join(new_dir, os.path.basename(filepath))
        os.rename(filepath, new_path)

        # Try to show it
        # This is expected to FAIL with current logic if optimization is strict and not recursive
        found_path = tasks.find_task_file(task_id)

        # With fix, it should find it
        self.assertIsNotNone(found_path, "Should find moved task in subdir with fixed logic")
        self.assertEqual(found_path, new_path)

    def test_list_tasks_subdir_bug(self):
        # Create task in foundation
        tasks.create_task("foundation", "Normal Task", "Desc")

        # Create task in foundation/subdir manually
        subdir = os.path.join(self.docs_dir, "foundation", "subdir")
        os.makedirs(subdir, exist_ok=True)

        # Copy the first task file to subdir with different ID
        files = [f for f in os.listdir(os.path.join(self.docs_dir, "foundation")) if f.endswith(".md")]
        src = os.path.join(self.docs_dir, "foundation", files[0])
        dst = os.path.join(subdir, "FOUNDATION-SUB-task.md")

        with open(src, "r") as f:
            content = f.read()
        # Hacky ID replace
        content = content.replace("id: " + content.split("id: ")[1].split()[0], "id: FOUNDATION-SUB")
        with open(dst, "w") as f:
            f.write(content)

        # List with category filter
        sys.stdout = StringIO()
        tasks.list_tasks(category="foundation", output_format="json")
        output = sys.stdout.getvalue()
        data = json.loads(output)

        ids = [t['id'] for t in data]
        # With fix, it should list it
        self.assertIn("FOUNDATION-SUB", ids, "Should list task in subdir with fixed logic")

    def test_archive_task(self):
        tasks.create_task("foundation", "Task to Archive", "Desc")
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_id = data[0]['id']
        filepath = data[0]['filepath']

        # Archive it
        sys.stdout = StringIO()
        tasks.archive_task(task_id, output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertTrue(output['success'])

        new_path = output['new_path']
        self.assertTrue(os.path.exists(new_path))
        self.assertFalse(os.path.exists(filepath))
        self.assertIn("archive", new_path)

        # Verify it is NOT listed by default
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        ids = [t['id'] for t in data]
        self.assertNotIn(task_id, ids)

        # Verify it IS listed with flag
        sys.stdout = StringIO()
        tasks.list_tasks(include_archived=True, output_format="json")
        data = json.loads(sys.stdout.getvalue())
        ids = [t['id'] for t in data]
        self.assertIn(task_id, ids)

    def test_enforce_dependencies(self):
        # Create Task A (Pending)
        tasks.create_task("foundation", "Task A", "Desc")
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_a = [t for t in data if t['title'] == "Task A"][0]
        task_a_id = task_a['id']

        # Create Task B (Depends on A)
        tasks.create_task("foundation", "Task B", "Desc", dependencies=[task_a_id])
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_b = [t for t in data if t['title'] == "Task B"][0]
        task_b_id = task_b['id']

        # Try to update Task B to in_progress -> Should FAIL because A is pending
        with self.assertRaises(SystemExit):
            # Suppress stderr to keep test output clean
            with patch('sys.stderr', new=StringIO()):
                tasks.update_task_status(task_b_id, "in_progress")

        # Verify status did not change
        sys.stdout = StringIO()
        tasks.show_task(task_b_id, output_format="json")
        task_b_updated = json.loads(sys.stdout.getvalue())
        self.assertNotEqual(task_b_updated['status'], "in_progress")

    def test_update_with_satisfied_dependencies(self):
        # Create Task A (Completed)
        tasks.create_task("foundation", "Task A", "Desc", status="completed")
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_a = [t for t in data if t['title'] == "Task A"][0]
        task_a_id = task_a['id']

        # Create Task B (Depends on A)
        tasks.create_task("foundation", "Task B", "Desc", dependencies=[task_a_id])
        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        task_b = [t for t in data if t['title'] == "Task B"][0]
        task_b_id = task_b['id']

        # Update Task B to in_progress -> Should SUCCEED
        tasks.update_task_status(task_b_id, "in_progress")

        # Verify status changed
        sys.stdout = StringIO()
        tasks.show_task(task_b_id, output_format="json")
        task_b_updated = json.loads(sys.stdout.getvalue())
        self.assertEqual(task_b_updated['status'], "in_progress")

if __name__ == "__main__":
    unittest.main()
