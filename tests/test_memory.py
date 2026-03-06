import unittest
import os
import sys
import tempfile
import json
from io import StringIO
from unittest.mock import patch
import datetime

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts")))
import memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.repo_root = self.test_dir.name
        self.docs_dir = os.path.join(self.repo_root, "docs", "memories")

        # Monkey patch global variables
        self.original_repo_root = memory.REPO_ROOT
        self.original_memory_dir = memory.MEMORY_DIR

        memory.REPO_ROOT = self.repo_root
        memory.MEMORY_DIR = self.docs_dir

        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        memory.REPO_ROOT = self.original_repo_root
        memory.MEMORY_DIR = self.original_memory_dir
        self.test_dir.cleanup()
        sys.stdout = self.held

    def test_create_and_list(self):
        memory.create_memory("Test Title", "Content", ["tag1"], output_format="json")
        output = sys.stdout.getvalue()
        self.assertIn('"success": true', output)

        sys.stdout = StringIO()
        memory.list_memories(output_format="json")
        output = sys.stdout.getvalue()
        data = json.loads(output)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], "Test Title")
        self.assertEqual(data[0]['tags'], ["tag1"])

    def test_read(self):
        memory.create_memory("Read Me", "Content", output_format="json")
        # Get filename
        sys.stdout = StringIO()
        memory.list_memories(output_format="json")
        data = json.loads(sys.stdout.getvalue())
        filename = data[0]['filename']

        sys.stdout = StringIO()
        memory.read_memory(filename, output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertIn("Content", output['content'])

    def test_index_memories(self):
        # Create a mock task with wikilinks
        task_dir = os.path.join(self.repo_root, "docs", "tasks", "foundation")
        os.makedirs(task_dir, exist_ok=True)
        task_file = os.path.join(task_dir, "FOUNDATION-001.md")
        with open(task_file, "w") as f:
            f.write("---\nid: FOUNDATION-001\n---\nHere is a wikilink to [[EntityA]] and another to [[EntityB]].")

        # Run index
        sys.stdout = StringIO()
        memory.index_memories(output_format="json")
        output = json.loads(sys.stdout.getvalue())
        self.assertTrue(output.get("success"))

        # Check entities.json
        entities_path = os.path.join(self.docs_dir, "entities.json")
        self.assertTrue(os.path.exists(entities_path))
        with open(entities_path, "r") as f:
            entities = json.load(f)

        self.assertIn("EntityA", entities)
        self.assertIn("FOUNDATION-001", entities["EntityA"])
        self.assertIn("EntityB", entities)
        self.assertIn("FOUNDATION-001", entities["EntityB"])

if __name__ == "__main__":
    unittest.main()
