import unittest
import os
import sys
import tempfile
import datetime
from io import StringIO
from unittest.mock import patch

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts import continuity

class TestContinuity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name

        # Monkey patch global variables in continuity module
        self.original_repo_root = continuity.REPO_ROOT
        self.original_continuity_dir = continuity.CONTINUITY_DIR
        self.original_ledgers_dir = continuity.LEDGERS_DIR
        self.original_handoffs_dir = continuity.HANDOFFS_DIR

        continuity.REPO_ROOT = self.repo_root
        continuity.CONTINUITY_DIR = os.path.join(self.repo_root, "docs", "continuity")
        continuity.LEDGERS_DIR = os.path.join(continuity.CONTINUITY_DIR, "ledgers")
        continuity.HANDOFFS_DIR = os.path.join(continuity.CONTINUITY_DIR, "handoffs")

        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        continuity.REPO_ROOT = self.original_repo_root
        continuity.CONTINUITY_DIR = self.original_continuity_dir
        continuity.LEDGERS_DIR = self.original_ledgers_dir
        continuity.HANDOFFS_DIR = self.original_handoffs_dir

        self.test_dir.cleanup()
        sys.stdout = self.held

    def test_ensure_dirs(self):
        continuity.ensure_dirs()
        self.assertTrue(os.path.exists(continuity.LEDGERS_DIR))
        self.assertTrue(os.path.exists(continuity.HANDOFFS_DIR))

    def test_create_entry_ledger(self):
        path = continuity.create_entry(continuity.LEDGERS_DIR, "My Ledger", "Content here", prefix="ledger-")
        self.assertTrue(os.path.exists(path))
        self.assertIn("ledger-", os.path.basename(path))

        with open(path, "r") as f:
            content = f.read()
            self.assertIn("title: \"My Ledger\"", content)
            self.assertIn("type: ledger", content)
            self.assertIn("Content here", content)

    def test_create_entry_handoff(self):
        path = continuity.create_entry(continuity.HANDOFFS_DIR, "My Handoff", "Content here", prefix="handoff-")
        self.assertTrue(os.path.exists(path))
        self.assertIn("handoff-", os.path.basename(path))

        with open(path, "r") as f:
            content = f.read()
            self.assertIn("type: handoff", content)

    def test_get_latest_file(self):
        # Create two files with different timestamps in filename
        # Our create_entry uses current time, so we might need to sleep or manually name
        continuity.ensure_dirs()

        # File 1: Old
        f1 = os.path.join(continuity.LEDGERS_DIR, "ledger-2023-01-01-120000-old.md")
        with open(f1, "w") as f: f.write("old")

        # File 2: New
        f2 = os.path.join(continuity.LEDGERS_DIR, "ledger-2023-01-02-120000-new.md")
        with open(f2, "w") as f: f.write("new")

        latest = continuity.get_latest_file(continuity.LEDGERS_DIR, prefix="ledger-")
        self.assertEqual(latest, f2)

    def test_read_file(self):
        path = continuity.create_entry(continuity.LEDGERS_DIR, "Title", "Secret Content", prefix="ledger-")
        content = continuity.read_file(path)
        self.assertIn("Secret Content", content)

        self.assertIsNone(continuity.read_file("nonexistent"))

if __name__ == "__main__":
    unittest.main()
