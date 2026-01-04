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

from scripts.lib import io, config, audit, concurrency

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
        
        # Ensure registry directory exists
        os.makedirs(self.registry_dir, exist_ok=True)

        lock_path = os.path.join(self.registry_dir, ".lock")
        try:
            with concurrency.FileLock(lock_path):
                path = os.path.join(self.registry_dir, f"{self.agent_id}.json")
                io.write_json(path, data)
        except Exception as e:
            # If locking fails, we might still want to try write or just log
            print(f"Warning: Could not acquire registry lock: {e}", file=sys.stderr)
            # Fallback to just writing (optimistic)
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
            
        # We don't lock for reading to avoid blocking readers, 
        # but we handle race conditions (file removed during iteration).
        for f in os.listdir(self.registry_dir):
            if f.endswith(".json"):
                try:
                    data = io.read_json(os.path.join(self.registry_dir, f))
                    agents.append(data)
                except:
                    pass
        return agents

    @audit.audit_log("agent_send")
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

    @audit.audit_log("agent_read")
    def read(self, limit=10):
        """Read messages from inbox."""
        mailbox = os.path.join(self.messages_dir, self.agent_id)
        public_box = os.path.join(self.messages_dir, "public")
        
        results = []
        
        # Helper to process a directory atomically
        # We move files to archive BEFORE reading to ensure exclusivity
        def process_box(source_dir, is_public=False):
            found_msgs = []
            if not os.path.exists(source_dir):
                return found_msgs
            
            # Snapshot of files
            try:
                files = sorted([f for f in os.listdir(source_dir) if f.endswith(".json")])
            except FileNotFoundError:
                return found_msgs

            for f in files:
                if len(found_msgs) + len(results) >= limit:
                    break
                    
                src_path = os.path.join(source_dir, f)
                
                # Check if it's our own public message before moving?
                # If we move it, we claim it. If it's ours, we might want to skip it?
                # But if we skip it, it stays in public for others.
                # If we claim it, we remove it from public.
                # Requirement: "Filter out own public messages"
                # If we filter it out, we don't move it.
                if is_public:
                    try:
                        # Peek to see sender (non-atomic peek, but safe optimization)
                        # If we race here, worst case we try to move it and fail, or move it and then realize it's ours.
                        # If it's ours, we should probably NOT move it, so others can read it?
                        # Wait, "Filter out own public messages" usually implies "Don't process messages I sent".
                        # But if I don't process it, does it stay there?
                        # If public is a work queue, someone else must process it.
                        # If I am the sender, I shouldn't consume my own task? 
                        # Assuming yes. So I skip.
                        
                        # Optimization: Check sender from filename if encoded? No, it's inside.
                        # We have to read it.
                        data_peek = io.read_json(src_path)
                        if data_peek.get("from") == self.agent_id:
                            continue
                    except:
                        # File gone or unreadable
                        continue

                # Prepare archive destination
                # For public, we might want a 'claimed_by_me' folder, but standard 'archive' folder 
                # in the source directory implies "processed by the system".
                # If public is shared, 'archive' is a shared processed folder.
                archive_dir = os.path.join(source_dir, "archive")
                os.makedirs(archive_dir, exist_ok=True)
                dest_path = os.path.join(archive_dir, f)
                
                # Atomic Move
                try:
                    os.rename(src_path, dest_path)
                    # Successful claim
                    data = io.read_json(dest_path)
                    found_msgs.append(data)
                except OSError:
                    # Rename failed (someone else took it) or read failed
                    continue
            
            return found_msgs

        # Process private messages
        # Private messages don't strictly need atomic move-before-read if single consumer,
        # but it keeps consistency with "at most once" processing.
        results.extend(process_box(mailbox, is_public=False))
        
        # Process public messages (only if limit not reached)
        if len(results) < limit:
             # Adjust limit for public processing
             # Actually process_box checks global limit logic roughly
             public_results = process_box(public_box, is_public=True)
             results.extend(public_results)

        # Sort combined results by timestamp
        results.sort(key=lambda x: x["timestamp"])
        
        return results[:limit]

    def prune_registry(self, ttl_minutes=60):
        """Remove stale agent registrations."""
        now = datetime.datetime.now()
        removed = []
        
        # Ensure registry directory exists
        if not os.path.exists(self.registry_dir):
            return []

        lock_path = os.path.join(self.registry_dir, ".lock")
        
        try:
            with concurrency.FileLock(lock_path):
                for f in os.listdir(self.registry_dir):
                    if not f.endswith(".json"):
                        continue
                        
                    path = os.path.join(self.registry_dir, f)
                    try:
                        # Read without lock? We have the directory lock.
                        data = io.read_json(path)
                        last_seen = datetime.datetime.fromisoformat(data["last_seen"])
                        if (now - last_seen).total_seconds() > ttl_minutes * 60:
                            os.remove(path)
                            removed.append(data['id'])
                    except:
                        pass
        except Exception as e:
            print(f"Error during prune_registry: {e}", file=sys.stderr)
            
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