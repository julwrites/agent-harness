import unittest
import os
import sys
import json
from unittest.mock import patch, mock_open, MagicMock

# Add repo root to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(REPO_ROOT)

from scripts import code_index

class TestCodeIndex(unittest.TestCase):

    def setUp(self):
        self.sample_python_code = """
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass

my_global = 10
"""

    def test_parse_python_file(self):
        with patch("builtins.open", mock_open(read_data=self.sample_python_code)):
            symbols = code_index.parse_python_file("dummy.py")

        self.assertEqual(len(symbols), 4)

        names = [s["name"] for s in symbols]
        self.assertIn("MyClass", names)
        self.assertIn("MyClass.my_method", names)
        self.assertIn("my_function", names)
        self.assertIn("my_global", names)

        types = {s["name"]: s["type"] for s in symbols}
        self.assertEqual(types["MyClass"], "class")
        self.assertEqual(types["MyClass.my_method"], "method")
        self.assertEqual(types["my_function"], "function")
        self.assertEqual(types["my_global"], "variable")

    @patch("scripts.code_index.get_source_roots")
    @patch("os.walk")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_index_code(self, mock_json_dump, mock_file, mock_walk, mock_get_roots):
        mock_get_roots.return_value = ["/root/src"]

        # Mock file system
        mock_walk.return_value = [
            ("/root/src", [], ["main.py", "utils.js"])
        ]

        # Mock file content for parsing
        mock_file.side_effect = [
            mock_open(read_data="def main(): pass").return_value, # for main.py
            # open for json dump is handled by mock_file context manager usually, but here side_effect makes it tricky
            # Let's simplify and just check that json.dump was called with expected structure
            MagicMock() # For the write call
        ]

        # We need to ensure open() returns a file object that can be read for main.py
        # And a file object that can be written for json.dump

        # Simpler approach: Mock parse_python_file
        with patch("scripts.code_index.parse_python_file") as mock_parse:
            mock_parse.return_value = [{"name": "main", "type": "function", "line": 1}]

            # Since we mock parse_python_file, open() is only called for writing the index
            # But wait, os.walk returns files, loop checks endswith .py, then calls parse_python_file.
            # parse_python_file calls open.

            code_index.index_code()

            # Check if json.dump was called
            self.assertTrue(mock_json_dump.called)
            args, _ = mock_json_dump.call_args
            data = args[0]

            self.assertIn("files", data)
            self.assertIn("symbols", data)

            # rel path depends on what REPO_ROOT is resolved to in the script vs test
            # In the script, REPO_ROOT is global. We should probably patch it or ensure consistency.
            # But the script uses os.path.relpath(filepath, REPO_ROOT)

            # Let's inspect the keys in 'files'
            # Assuming REPO_ROOT is /root (or similar relative base)
            # The key should be relative path.

            self.assertTrue(len(data["files"]) > 0)

            # Verify symbol index
            self.assertIn("main", data["symbols"])
            self.assertEqual(data["symbols"]["main"][0]["line"], 1)

    @patch("scripts.code_index.load_index")
    def test_search_symbols(self, mock_load):
        mock_load.return_value = {
            "symbols": {
                "MyClass": [{"file": "src/cls.py", "line": 10, "type": "class"}],
                "my_func": [{"file": "src/func.py", "line": 5, "type": "function"}]
            }
        }

        results = code_index.search_symbols("Class")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["symbol"], "MyClass")

        results = code_index.search_symbols("func")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["symbol"], "my_func")

        results = code_index.search_symbols("nonexistent")
        self.assertEqual(len(results), 0)

    @patch("scripts.code_index.load_index")
    def test_lookup_file(self, mock_load):
        mock_load.return_value = {
            "files": {
                "src/main.py": {"symbols": [{"name": "main", "type": "function", "line": 1}]}
            }
        }

        # Exact match
        result = code_index.lookup_file("src/main.py")
        self.assertIsNotNone(result)
        self.assertEqual(result["symbols"][0]["name"], "main")

        # Fuzzy match
        result = code_index.lookup_file("main.py")
        self.assertIsNotNone(result)

        # No match
        result = code_index.lookup_file("other.py")
        self.assertIsNone(result)

    @patch("scripts.code_index.get_source_roots")
    @patch("os.walk")
    @patch("builtins.open", new_callable=mock_open)
    def test_find_references(self, mock_file, mock_walk, mock_get_roots):
        mock_get_roots.return_value = ["/root"]
        mock_walk.return_value = [
             ("/root", [], ["test.py"])
        ]

        mock_file.return_value = mock_open(read_data="a = 1\nprint(target_symbol)\n# comment with target_symbol").return_value

        # Use an iterator for readlines to simulate file reading
        # mock_open read_data handles iteration automatically

        refs = code_index.find_references("target_symbol")

        self.assertEqual(len(refs), 2)
        self.assertEqual(refs[0]["line"], 2)
        self.assertEqual(refs[1]["line"], 3)

if __name__ == "__main__":
    unittest.main()
