#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts import tasks
from scripts import comm

class Orchestrator:
    def __init__(self, agent_id="orchestrator"):
        self.agent_id = agent_id
        self.comm_bus = comm.Comm(agent_id=self.agent_id, role="orchestrator")
        self.comm_bus.register()

    def get_pending_tasks(self):
        """Retrieve tasks with 'pending' status."""
        # Using tasks module directly. list_tasks can return list of dicts.
        pending = tasks.list_tasks(status="pending", output_format="json")
        if isinstance(pending, str):
            try:
                pending = json.loads(pending)
            except json.JSONDecodeError:
                pending = []
        return pending

    def assign_tasks(self):
        """Assign pending tasks to available agents."""
        pending_tasks = self.get_pending_tasks()
        if not pending_tasks:
            return 0

        agents = self.comm_bus.list_agents()
        available_agents = [a for a in agents if a.get("id") != self.agent_id]
        if not available_agents:
            return 0

        assigned_count = 0
        for task in pending_tasks:
            # Simple round-robin or greedy assignment
            agent = available_agents[assigned_count % len(available_agents)]
            agent_id = agent.get("id")

            # Send message to agent
            msg_content = json.dumps({"task_id": task["id"], "action": "execute"})
            self.comm_bus.send(recipient_id=agent_id, content=msg_content, type="task_assignment", request_receipt=True)

            # Update task status to in_progress
            tasks.update_task_status(task["id"], "in_progress", output_format="json")
            assigned_count += 1

        return assigned_count

    def monitor(self):
        """Monitor messages for task completions and update statuses."""
        messages = self.comm_bus.read()
        processed_count = 0
        for msg in messages:
            msg_type = msg.get("type", "")
            content = msg.get("content", "")

            if msg_type == "task_completion":
                try:
                    data = json.loads(content)
                    task_id = data.get("task_id")
                    if task_id:
                        tasks.update_task_status(task_id, "completed", output_format="json")
                        processed_count += 1
                except json.JSONDecodeError:
                    pass
        return processed_count

    def run(self, interval=5):
        """Unified loop to repeatedly assign tasks and monitor."""
        print(f"Orchestrator {self.agent_id} starting run loop. Press Ctrl+C to stop.")
        try:
            while True:
                assigned = self.assign_tasks()
                if assigned > 0:
                    print(f"Assigned {assigned} tasks.")

                processed = self.monitor()
                if processed > 0:
                    print(f"Processed {processed} completion messages.")

                time.sleep(interval)
        except KeyboardInterrupt:
            print("Orchestrator stopped.")

def main():
    parser = argparse.ArgumentParser(description="Subagent Orchestrator")
    subparsers = parser.add_subparsers(dest="command")

    # Assign
    subparsers.add_parser("assign", help="Assign pending tasks to available agents once")

    # Monitor
    subparsers.add_parser("monitor", help="Check for completion messages once")

    # Run
    run_parser = subparsers.add_parser("run", help="Run the orchestrator loop")
    run_parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")

    args = parser.parse_args()

    orchestrator = Orchestrator()

    if args.command == "assign":
        count = orchestrator.assign_tasks()
        print(f"Assigned {count} tasks.")
    elif args.command == "monitor":
        count = orchestrator.monitor()
        print(f"Processed {count} messages.")
    elif args.command == "run":
        orchestrator.run(interval=args.interval)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
