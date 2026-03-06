import unittest
import os
import sys
import tempfile
import json
import shutil
import subprocess

# Add repo root to path
test_file_path = os.path.abspath(__file__)
repo_root = os.path.dirname(os.path.dirname(test_file_path))
if repo_root not in sys.path:
    sys.path.append(repo_root)

from scripts import tdd

class TestTDDEnforcer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, ".tdd_state_test.json")
        self.original_dir = os.getcwd()
        os.chdir(self.temp_dir)

        # Initialize an empty git repo to test git diff
        subprocess.run(["git", "init"], capture_output=True)
        # Create a mock test environment
        os.makedirs("tests")
        os.makedirs("src")

        with open("tests/test_dummy.py", "w") as f:
            f.write("import unittest\nclass TestDummy(unittest.TestCase):\n    def test_pass(self):\n        self.assertTrue(True)\n")

        with open("src/dummy.py", "w") as f:
            f.write("def dummy():\n    return True\n")

        subprocess.run(["git", "add", "."], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], capture_output=True)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

    def test_get_set_state(self):
        # Default state (file doesn't exist)
        state = tdd.get_state(self.state_file)
        self.assertEqual(state, tdd.TDDState.RED)

        # Change state
        tdd.set_state(tdd.TDDState.GREEN, self.state_file)
        state = tdd.get_state(self.state_file)
        self.assertEqual(state, tdd.TDDState.GREEN)

if __name__ == '__main__':
    unittest.main()
