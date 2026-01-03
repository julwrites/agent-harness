import unittest
import os
import sys
import tempfile
import json
from io import StringIO
from unittest.mock import patch, MagicMock

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts import index

class TestIndex(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name
        self.index_file = os.path.join(self.repo_root, "docs", "INDEX.yaml")

        # Monkey patch global variables in index module
        self.original_repo_root = index.REPO_ROOT
        self.original_index_file = index.INDEX_FILE

        index.REPO_ROOT = self.repo_root
        index.INDEX_FILE = self.index_file

        # Ensure docs dir exists for index
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)

        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        index.REPO_ROOT = self.original_repo_root
        index.INDEX_FILE = self.original_index_file
        self.test_dir.cleanup()
        sys.stdout = self.held

    def test_init_index(self):
        index.init_index()
        self.assertTrue(os.path.exists(self.index_file))

        # Run again, should not fail
        index.init_index()
        output = sys.stdout.getvalue()
        self.assertIn("Index already exists", output)

    def test_add_entry(self):
        index.init_index()

        # Create a dummy file
        dummy_file = os.path.join(self.repo_root, "test.md")
        with open(dummy_file, "w") as f:
            f.write("content")

        # Add entry
        index.add_entry("test.md", related=["other.md"], depends_on=["dep.md"], force=True)

        with open(self.index_file, "r") as f:
            content = f.read()
            self.assertIn("test.md:", content)
            self.assertIn("related:", content)
            self.assertIn("other.md", content)
            self.assertIn("depends_on:", content)
            self.assertIn("dep.md", content)

    def test_remove_entry(self):
        index.init_index()
        index.add_entry("test.md", force=True)

        index.remove_entry("test.md")

        with open(self.index_file, "r") as f:
            content = f.read()
            self.assertNotIn("test.md:", content)

    def test_remove_entry_item(self):
        index.init_index()
        index.add_entry("test.md", related=["rel1"], force=True)

        index.remove_entry("test.md", item="rel1", section="related")

        with open(self.index_file, "r") as f:
            content = f.read()
            self.assertIn("test.md:", content)
            self.assertNotIn("rel1", content)

    def test_check_integrity(self):
        index.init_index()
        # Case 1: Integrity Check Fails
        # Note: SimpleYaml parses "related: []" as a string "[]" instead of empty list.
        # We must use correct format for empty lists (just empty value or omit)
        # However, to trigger integrity error, we want it to point to non-existent files.
        with open(self.index_file, "w") as f:
            f.write("invalid.md:\n  related:\n  - missing_rel.md\n  depends_on:\n  - missing_dep.md\n")

        with self.assertRaises(SystemExit):
             index.check_integrity()

        # Case 2: Integrity Check Passes
        # Clear stdout
        sys.stdout = StringIO()

        # Overwrite index with a valid one or clear it
        # Since SimpleYaml.save overwrites, we can just init or add properly
        # But first, let's fix the file system state to match the "invalid" index, effectively making it valid
        with open(os.path.join(self.repo_root, "invalid.md"), "w") as f:
            f.write("ok")

        # Now it should pass because "invalid.md" exists
        index.check_integrity()
        output = sys.stdout.getvalue()
        self.assertIn("Index integrity check passed", output)

    def test_get_impact(self):
        index.init_index()
        # A depends on B
        index.add_entry("A.md", depends_on=["B.md"], force=True)
        index.add_entry("B.md", force=True)

        # Check impact of B.md
        sys.stdout = StringIO()
        index.get_impact("B.md", output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertIn("A.md", output)

    def test_visualize(self):
        index.init_index()
        index.add_entry("A.md", depends_on=["B.md"], force=True)

        sys.stdout = StringIO()
        index.visualize(output_format="text")
        output = sys.stdout.getvalue()
        self.assertIn("graph TD", output)
        self.assertIn("A.md", output)
        self.assertIn("B.md", output)

    def test_list_entries(self):
        index.init_index()
        index.add_entry("A.md", force=True)

        sys.stdout = StringIO()
        index.list_entries(output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertIn("A.md", output)

if __name__ == "__main__":
    unittest.main()
