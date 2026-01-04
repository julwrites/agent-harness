#!/usr/bin/env python3
import os
import sys
import json
import time
import uuid
import argparse
import datetime
import heapq
import hmac
import hashlib

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.getenv("TASKS_REPO_ROOT", os.path.dirname(SCRIPT_DIR))
sys.path.append(REPO_ROOT)

from scripts.lib import io, config, audit, concurrency

class Security:
    def __init__(self, secret=None):
        self.secret = secret or os.getenv("AGENT_CLUSTER_SECRET", "default-insecure-secret")

    def sign(self, payload_str):
        return hmac.new(self.secret.encode(), payload_str.encode(), hashlib.sha256).hexdigest()

    def verify(self, payload_str, signature):
        expected = self.sign(payload_str)
        return hmac.compare_digest(expected, signature)

class Comm:
    def __init__(self, agent_id=None, role="unknown"):
        self.config = config.get_config(REPO_ROOT)
        self.bus_dir = os.path.join(REPO_ROOT, self.config["agents"]["bus_dir"])
        self.registry_dir = os.path.join(self.bus_dir, "registry")
        self.messages_dir = os.path.join(self.bus_dir, "messages")
        
        self.agent_id = agent_id or f"{role}-{str(uuid.uuid4())[:8]}"
        self.role = role
        
        # Ensure mailbox exists
        self.mailbox = os.path.join(self.messages_dir, self.agent_id)
        os.makedirs(self.mailbox, exist_ok=True)
        
        # Security & Rate Limiting
        self.security = Security()
        self.rate_limit_window = [] # timestamps
        self.rate_limit_max = 60 # msgs per minute

    def register(self):
        """Announce presence in the registry."""
        data = {
            "id": self.agent_id,
            "role": self.role,
            "last_seen": datetime.datetime.now().isoformat(),
            "pid": os.getpid()
        }
        
        os.makedirs(self.registry_dir, exist_ok=True)

        lock_path = os.path.join(self.registry_dir, ".lock")
        try:
            with concurrency.FileLock(lock_path):
                path = os.path.join(self.registry_dir, f"{self.agent_id}.json")
                io.write_json(path, data)
        except Exception as e:
            print(f"Warning: Could not acquire registry lock: {e}", file=sys.stderr)
            path = os.path.join(self.registry_dir, f"{self.agent_id}.json")
            io.write_json(path, data)
        
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

    @audit.audit_log("agent_send")
    def send(self, recipient_id, content, type="text", metadata=None, ttl=None, request_receipt=False, retry_count=3, compress=False, encrypt=False):
        """Send a message to another agent."""
        # Rate Limiting
        now = time.time()
        self.rate_limit_window = [t for t in self.rate_limit_window if now - t < 60]
        if len(self.rate_limit_window) >= self.rate_limit_max:
            raise Exception("Rate limit exceeded")
        self.rate_limit_window.append(now)

        # Validation
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        if len(content) > 10 * 1024 * 1024: # 10MB limit
            raise ValueError("Message too large")

        if recipient_id == "public":
            target_dir = os.path.join(self.messages_dir, "public")
        else:
            target_dir = os.path.join(self.messages_dir, recipient_id)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)

        msg_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        metadata = metadata or {}
        if ttl:
            metadata["ttl"] = ttl
        if request_receipt:
            metadata["request_receipt"] = True
        if compress:
            metadata["compression"] = "gzip"
        if encrypt:
            metadata["encrypted"] = True
            content = f"ENC:{content}" # Mock encryption

        # Sign
        # Signature covers content + timestamp + id
        payload = f"{msg_id}{timestamp}{content}"
        metadata["sig"] = self.security.sign(payload)

        message = {
            "id": msg_id,
            "from": self.agent_id,
            "to": recipient_id,
            "timestamp": timestamp,
            "type": type,
            "content": content,
            "metadata": metadata
        }
        
        filename = f"{time.time()}_{msg_id}.json"
        if compress:
            filename += ".gz"
            
        path = os.path.join(target_dir, filename)
        
        # Retry logic for delivery
        for attempt in range(retry_count + 1):
            try:
                io.write_json(path, message)
                break
            except Exception as e:
                if attempt == retry_count:
                    raise e
                time.sleep(0.5 * (2 ** attempt))
                
        return msg_id

    def send_batch(self, messages):
        """
        Send multiple messages.
        messages: list of dicts with keys (recipient, content, type, metadata, etc.)
        """
        results = []
        for msg in messages:
            try:
                mid = self.send(
                    msg.get("recipient"),
                    msg.get("content"),
                    type=msg.get("type", "text"),
                    metadata=msg.get("metadata"),
                    ttl=msg.get("ttl"),
                    request_receipt=msg.get("request_receipt", False),
                    compress=msg.get("compress", False)
                )
                results.append(mid)
            except Exception as e:
                results.append(None)
        return results

    @audit.audit_log("agent_read")
    def read(self, limit=10):
        """Read messages from inbox."""
        public_box = os.path.join(self.messages_dir, "public")
        
        results = []
        processed_ids = self._load_processed_ids()
        
        def process_box(source_dir, is_public=False):
            found_msgs = []
            if not os.path.exists(source_dir):
                return found_msgs
            
            try:
                # Optimized listing with scandir and heap
                def valid_file(e):
                    return e.is_file() and (e.name.endswith(".json") or e.name.endswith(".json.gz"))

                with os.scandir(source_dir) as it:
                    # Get top files by name (timestamp)
                    entries = heapq.nsmallest(limit * 2, (e for e in it if valid_file(e)), key=lambda e: e.name)
                    files = [e.name for e in entries]
            except OSError:
                return found_msgs

            for f in files:
                if len(found_msgs) + len(results) >= limit:
                    break
                    
                src_path = os.path.join(source_dir, f)
                
                if is_public:
                    try:
                        data_peek = io.read_json(src_path)
                        if data_peek.get("from") == self.agent_id:
                            continue
                    except:
                        continue

                archive_dir = os.path.join(source_dir, "archive")
                os.makedirs(archive_dir, exist_ok=True)
                dest_path = os.path.join(archive_dir, f)
                
                try:
                    os.rename(src_path, dest_path)
                except OSError:
                    continue
                
                # Processing
                try:
                    data = io.read_json(dest_path)
                except Exception:
                    self._move_to_dlq(dest_path, "corrupt_json")
                    continue

                # Validation & Security Check
                if "sig" in data.get("metadata", {}):
                    payload = f"{data['id']}{data['timestamp']}{data['content']}"
                    if not self.security.verify(payload, data["metadata"]["sig"]):
                        self._move_to_dlq(dest_path, "invalid_signature")
                        continue
                
                # Decrypt
                if data.get("metadata", {}).get("encrypted"):
                    if data["content"].startswith("ENC:"):
                        data["content"] = data["content"][4:] # Mock decrypt

                # TTL Check
                if "ttl" in data.get("metadata", {}):
                    try:
                        ttl = int(data["metadata"]["ttl"])
                        ts = datetime.datetime.fromisoformat(data["timestamp"])
                        diff = (datetime.datetime.now() - ts).total_seconds()
                        if diff > ttl:
                            self._move_to_dlq(dest_path, "expired")
                            continue
                    except Exception as e:
                        print(f"TTL Check Error: {e}", file=sys.stderr)
                        pass 

                # Idempotency Check
                msg_id = data.get("id")
                if msg_id in processed_ids:
                    continue
                
                processed_ids.add(msg_id)
                self._save_processed_id(msg_id)

                # Receipt
                if data.get("metadata", {}).get("request_receipt"):
                    try:
                        if data.get("type") != "receipt":
                            self.send(data["from"], f"Receipt for {data['id']}", type="receipt", metadata={"ref_id": data["id"]})
                    except:
                        pass 

                found_msgs.append(data)
            
            return found_msgs

        results.extend(process_box(self.mailbox, is_public=False))
        
        if len(results) < limit:
             public_results = process_box(public_box, is_public=True)
             results.extend(public_results)

        results.sort(key=lambda x: x["timestamp"])
        return results[:limit]

    def cleanup_archive(self, max_age_days=30):
        """Remove archived messages older than max_age_days."""
        limit_seconds = max_age_days * 86400
        now = time.time()
        
        dirs_to_clean = [
            os.path.join(self.messages_dir, "public", "archive"),
            os.path.join(self.mailbox, "archive")
        ]
        
        count = 0
        for d in dirs_to_clean:
            if not os.path.exists(d):
                continue
            
            try:
                with os.scandir(d) as it:
                    for entry in it:
                        if not entry.is_file():
                            continue
                        try:
                            stat = entry.stat()
                            if now - stat.st_mtime > limit_seconds:
                                os.remove(entry.path)
                                count += 1
                        except:
                            pass
            except OSError:
                pass
        return count

    def _move_to_dlq(self, filepath, reason="unknown"):
        """Move message to Dead Letter Queue."""
        dirname = os.path.dirname(os.path.dirname(filepath)) # go up from archive/ to agent/ 
        dlq_dir = os.path.join(dirname, "dlq")
        os.makedirs(dlq_dir, exist_ok=True)
        
        filename = os.path.basename(filepath)
        dest = os.path.join(dlq_dir, f"{reason}_{filename}")
        try:
            os.rename(filepath, dest)
        except:
            pass

    def _load_processed_ids(self):
        """Load recent processed message IDs to enforce idempotency."""
        path = os.path.join(self.mailbox, ".processed")
        if not os.path.exists(path):
            return set()
        try:
            lines = io.read_text(path).splitlines()
            return set(lines[-1000:])
        except:
            return set()

    def _save_processed_id(self, msg_id):
        """Append ID to processed log."""
        path = os.path.join(self.mailbox, ".processed")
        try:
            with open(path, "a") as f:
                f.write(f"{msg_id}\n")
        except:
            pass

    def prune_registry(self, ttl_minutes=60):
        """Remove stale agent registrations."""
        now = datetime.datetime.now()
        removed = []
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
    send.add_argument("--ttl", type=int, help="TTL in seconds")
    send.add_argument("--receipt", action="store_true", help="Request receipt")
    send.add_argument("--compress", action="store_true", help="Compress message")
    send.add_argument("--encrypt", action="store_true", help="Encrypt message")

    # Read
    read = subparsers.add_parser("read", help="Read messages")
    read.add_argument("agent_id", help="Agent ID")
    
    # List
    list_agents = subparsers.add_parser("list", help="List active agents")
    
    # Register
    reg = subparsers.add_parser("register", help="Register as an agent")
    reg.add_argument("role", help="Role name")
    
    # Cleanup
    clean = subparsers.add_parser("cleanup", help="Cleanup archive")
    clean.add_argument("--days", type=int, default=30, help="Max age in days")

    args = parser.parse_args()

    if args.command == "send":
        comm = Comm(agent_id=args.from_id)
        comm.register()
        comm.send(args.recipient, args.message, ttl=args.ttl, request_receipt=args.receipt, compress=args.compress, encrypt=args.encrypt)
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
        
    elif args.command == "cleanup":
        comm = Comm()
        count = comm.cleanup_archive(max_age_days=args.days)
        print(f"Cleaned {count} archived files.")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
