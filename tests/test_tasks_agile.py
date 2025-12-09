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

class TestTasksAgile(unittest.TestCase):
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

    def test_create_agile_task(self):
        tasks.create_task(
            "features",
            "Agile Story",
            "As a user...",
            task_type="story",
            sprint="Sprint 1",
            estimate="5"
        )

        files = os.listdir(os.path.join(self.docs_dir, "features"))
        task_files = [f for f in files if f.endswith(".md") and f != ".keep"]
        self.assertEqual(len(task_files), 1)

        with open(os.path.join(self.docs_dir, "features", task_files[0]), "r") as f:
            content = f.read()
            self.assertIn("type: story", content)
            self.assertIn("sprint: Sprint 1", content)
            self.assertIn("estimate: 5", content)

    def test_list_by_sprint(self):
        tasks.create_task("features", "S1 Task", "Desc", sprint="Sprint 1")
        tasks.create_task("features", "S2 Task", "Desc", sprint="Sprint 2")

        sys.stdout = StringIO()
        tasks.list_tasks(sprint="Sprint 1", output_format="json")
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "S1 Task")

    def test_next_task_priority(self):
        # Create 3 tasks
        # 1. High Priority, Story (Score: Med + HighPrio + Story)
        # 2. Medium Priority, Task (Score: Med + MedPrio + Task)
        # 3. In Progress (Score: High)

        tasks.create_task("foundation", "T1", "Desc", priority="high", task_type="story")
        tasks.create_task("foundation", "T2", "Desc", priority="medium", task_type="task")
        tasks.create_task("foundation", "T3", "Desc", priority="low", status="in_progress")

        sys.stdout = StringIO()
        tasks.get_next_task(output_format="json")
        best = json.loads(sys.stdout.getvalue())

        # T3 should win because it is in_progress (+1000)
        self.assertEqual(best["title"], "T3")

        # Now complete T3
        tasks.update_task_status(best["id"], "completed")

        sys.stdout = StringIO()
        tasks.get_next_task(output_format="json")
        best = json.loads(sys.stdout.getvalue())

        # Now T1 should win (High Prio + Story > Medium Prio + Task)
        self.assertEqual(best["title"], "T1")

    def test_next_task_dependency_blocking(self):
        # T1 depends on T2
        tasks.create_task("foundation", "T1", "Desc", priority="high")
        # I need to get the ID of T1, but create_task returns None (prints output).
        # So I list them to find IDs.

        sys.stdout = StringIO()
        tasks.list_tasks(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        t1_id = data[0]["id"]

        # Create T2 depending on T1
        tasks.create_task("foundation", "T2", "Desc", priority="low", dependencies=[t1_id])

        # T1 is pending. T2 depends on T1.
        # Next task should be T1 (unblocked), not T2 (blocked by T1)

        sys.stdout = StringIO()
        tasks.get_next_task(output_format="json")
        best = json.loads(sys.stdout.getvalue())

        self.assertEqual(best["id"], t1_id)

if __name__ == "__main__":
    unittest.main()
