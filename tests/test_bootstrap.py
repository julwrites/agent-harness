import unittest
import os
import sys
import tempfile

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
import tasks

class TestBootstrap(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name
        self.docs_dir = os.path.join(self.repo_root, "docs", "tasks")

        # Monkey patch global variables
        self.original_repo_root = tasks.REPO_ROOT
        self.original_docs_dir = tasks.DOCS_DIR

        tasks.REPO_ROOT = self.repo_root
        tasks.DOCS_DIR = self.docs_dir

    def tearDown(self):
        tasks.REPO_ROOT = self.original_repo_root
        tasks.DOCS_DIR = self.original_docs_dir
        self.test_dir.cleanup()

    def test_init_creates_new_dirs(self):
        # Suppress output
        from io import StringIO
        held, sys.stdout = sys.stdout, StringIO()

        try:
            tasks.init_docs()
        finally:
            sys.stdout = held

        # Check memories
        self.assertTrue(os.path.exists(os.path.join(self.repo_root, "docs", "memories")))
        self.assertTrue(os.path.exists(os.path.join(self.repo_root, "docs", "memories", ".keep")))

        # Check security
        security_readme = os.path.join(self.repo_root, "docs", "security", "README.md")
        self.assertTrue(os.path.exists(security_readme))
        with open(security_readme, "r") as f:
            content = f.read()
            self.assertIn("Risk Assessment", content)

        # Check security tasks
        self.assertTrue(os.path.exists(os.path.join(self.docs_dir, "security")))

if __name__ == "__main__":
    unittest.main()
