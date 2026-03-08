import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(REPO_ROOT)

from scripts import orchestrator
from scripts import tasks
from scripts import comm

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        with patch('scripts.comm.Comm.register'):
            self.orch = orchestrator.Orchestrator()

    @patch('scripts.tasks.list_tasks')
    def test_get_pending_tasks(self, mock_list_tasks):
        mock_tasks = [{"id": "TASK-1", "status": "pending"}]
        mock_list_tasks.return_value = mock_tasks

        pending = self.orch.get_pending_tasks()

        mock_list_tasks.assert_called_once_with(status="pending", output_format="json")
        self.assertEqual(pending, mock_tasks)

    @patch('scripts.tasks.list_tasks')
    def test_get_pending_tasks_string_response(self, mock_list_tasks):
        mock_tasks = [{"id": "TASK-1", "status": "pending"}]
        mock_list_tasks.return_value = json.dumps(mock_tasks)

        pending = self.orch.get_pending_tasks()

        mock_list_tasks.assert_called_once_with(status="pending", output_format="json")
        self.assertEqual(pending, mock_tasks)

    @patch.object(orchestrator.Orchestrator, 'get_pending_tasks')
    @patch('scripts.comm.Comm.list_agents')
    @patch('scripts.comm.Comm.send')
    @patch('scripts.tasks.update_task_status')
    def test_assign_tasks(self, mock_update, mock_send, mock_list_agents, mock_get_pending):
        mock_get_pending.return_value = [{"id": "TASK-1", "status": "pending"}]
        mock_list_agents.return_value = [{"id": "agent-1", "role": "worker"}]

        count = self.orch.assign_tasks()

        self.assertEqual(count, 1)
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        self.assertEqual(kwargs['recipient_id'], "agent-1")
        self.assertEqual(kwargs['type'], "task_assignment")
        mock_update.assert_called_once_with("TASK-1", "in_progress", output_format="json")

    @patch('scripts.comm.Comm.read')
    @patch('scripts.tasks.update_task_status')
    def test_monitor(self, mock_update, mock_read):
        mock_read.return_value = [
            {"type": "task_completion", "content": json.dumps({"task_id": "TASK-1"})},
            {"type": "other", "content": "hello"}
        ]

        count = self.orch.monitor()

        self.assertEqual(count, 1)
        mock_update.assert_called_once_with("TASK-1", "completed", output_format="json")

if __name__ == '__main__':
    unittest.main()
