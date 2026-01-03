#!/usr/bin/env python3
import os
import sys
import json
import time
import uuid
import argparse
import datetime

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts.lib import io, config

class Comm:
    def __init__(self, agent_id=None, role="unknown"):
        self.config = config.get_config(REPO_ROOT)
        self.bus_dir = os.path.join(REPO_ROOT, self.config["agents"]["bus_dir"])
        self.registry_dir = os.path.join(self.bus_dir, "registry")
        self.messages_dir = os.path.join(self.bus_dir, "messages")
        
        self.agent_id = agent_id or f"{role}-{str(uuid.uuid4())[:8]}"
        self.role = role

    def register(self):
        """Announce presence in the registry."""
        data = {
            "id": self.agent_id,
            "role": self.role,
            "last_seen": datetime.datetime.now().isoformat(),
            "pid": os.getpid()
        }
        path = os.path.join(self.registry_dir, f"{self.agent_id}.json")
        io.write_json(path, data)
        
        # Ensure mailbox exists
        mailbox = os.path.join(self.messages_dir, self.agent_id)
        os.makedirs(mailbox, exist_ok=True)
        return self.agent_id

    def list_agents(self):
        """List active agents."""
        agents = []
        if not os.path.exists(self.registry_dir):
            return []
            
        for f in os.listdir(self.registry_dir):
            if f.endswith(".json"):
                try:
                    data = io.read_json(os.path.join(self.registry_dir, f))
                    agents.append(data)
                except:
                    pass
        return agents

    def send(self, recipient_id, content, type="text", metadata=None):
        """Send a message to another agent."""
        if recipient_id == "public":
            target_dir = os.path.join(self.messages_dir, "public")
        else:
            target_dir = os.path.join(self.messages_dir, recipient_id)
            if not os.path.exists(target_dir):
                # Check if agent exists in registry to avoid sending into void?
                # For now, allow sending to offline agents (mailbox pattern)
                os.makedirs(target_dir, exist_ok=True)

        msg_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        message = {
            "id": msg_id,
            "from": self.agent_id,
            "to": recipient_id,
            "timestamp": timestamp,
            "type": type,
            "content": content,
            "metadata": metadata or {}
        }
        
        # Filename: timestamp_uuid.json for sorting
        filename = f"{time.time()}_{msg_id}.json"
        path = os.path.join(target_dir, filename)
        
        io.write_json(path, message)
        return msg_id

    def read(self, limit=10):
        """Read messages from inbox."""
        mailbox = os.path.join(self.messages_dir, self.agent_id)
        public_box = os.path.join(self.messages_dir, "public")
        
        messages = []
        
        # Helper to read dir
        def read_dir(d):
            found = []
            if os.path.exists(d):
                files = sorted([f for f in os.listdir(d) if f.endswith(".json")])
                for f in files:
                    try:
                        path = os.path.join(d, f)
                        data = io.read_json(path)
                        # Filter out own public messages
                        if data.get("from") == self.agent_id:
                            continue
                        
                        found.append((path, data))
                    except:
                        pass
            return found

        # Read private
        private_msgs = read_dir(mailbox)
        # Read public
        public_msgs = read_dir(public_box)
        
        # Merge and sort by timestamp
        all_msgs = private_msgs + public_msgs
        all_msgs.sort(key=lambda x: x[1]["timestamp"])
        
        # Process limit
        results = []
        for path, msg in all_msgs[:limit]:
            results.append(msg)
            # Auto-archive/delete logic?
            # For now, let's move to archive folder to avoid re-reading
            self._archive(path)
            
        return results

    def _archive(self, filepath):
        """Moves a processed message to archive."""
        # Archive is sibling to messages
        # messages/agent_id/file.json -> messages/agent_id/archive/file.json
        dirname = os.path.dirname(filepath)
        archive_dir = os.path.join(dirname, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        dest = os.path.join(archive_dir, filename)
        
        try:
            os.rename(filepath, dest)
        except OSError:
            pass

    def prune_registry(self, ttl_minutes=60):
        """Remove stale agent registrations."""
        now = datetime.datetime.now()
        removed = []
        for agent in self.list_agents():
            try:
                last_seen = datetime.datetime.fromisoformat(agent["last_seen"])
                if (now - last_seen).total_seconds() > ttl_minutes * 60:
                    path = os.path.join(self.registry_dir, f"{agent['id']}.json")
                    os.remove(path)
                    removed.append(agent['id'])
            except:
                pass
        return removed

def main():
    parser = argparse.ArgumentParser(description="Agent Communication Bus")
    subparsers = parser.add_subparsers(dest="command")

    # Send
    send = subparsers.add_parser("send", help="Send a message")
    send.add_argument("recipient", help="Agent ID or 'public'")
    send.add_argument("message", help="Text content")
    send.add_argument("--from-id", help="Sender ID", default="cli-user")

    # Read
    read = subparsers.add_parser("read", help="Read messages")
    read.add_argument("agent_id", help="Agent ID")
    
    # List
    list_agents = subparsers.add_parser("list", help="List active agents")
    
    # Register (mostly for testing CLI)
    reg = subparsers.add_parser("register", help="Register as an agent")
    reg.add_argument("role", help="Role name")

    args = parser.parse_args()

    if args.command == "send":
        comm = Comm(agent_id=args.from_id)
        comm.register() # Ensure sender exists
        comm.send(args.recipient, args.message)
        print("Message sent.")

    elif args.command == "read":
        comm = Comm(agent_id=args.agent_id)
        msgs = comm.read()
        print(json.dumps(msgs, indent=2))

    elif args.command == "list":
        comm = Comm()
        agents = comm.list_agents()
        print(json.dumps(agents, indent=2))

    elif args.command == "register":
        comm = Comm(role=args.role)
        aid = comm.register()
        print(f"Registered as {aid}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
