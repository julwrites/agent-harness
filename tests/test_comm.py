import unittest
import os
import shutil
import time
from scripts import comm

class TestComm(unittest.TestCase):
    def setUp(self):
        # Override config for testing is hard without mocking get_config
        # We will assume REPO_ROOT is correctly set by the test runner context
        # But we need to isolate the bus directory.
        
        # Monkey patch config for this test instance?
        # Better: Comm class allows overriding paths?
        # Current implementation relies on global config. 
        # Let's rely on atomic I/O ensuring we don't break things, 
        # but we should clean up created test agents.
        self.agent_a = comm.Comm(role="test-a")
        self.agent_b = comm.Comm(role="test-b")
        
        self.id_a = self.agent_a.register()
        self.id_b = self.agent_b.register()

    def tearDown(self):
        # Cleanup registry
        if os.path.exists(self.agent_a.registry_dir):
            for aid in [self.id_a, self.id_b]:
                p = os.path.join(self.agent_a.registry_dir, f"{aid}.json")
                if os.path.exists(p):
                    os.remove(p)

    def test_registration(self):
        agents = self.agent_a.list_agents()
        ids = [a["id"] for a in agents]
        self.assertIn(self.id_a, ids)
        self.assertIn(self.id_b, ids)

    def test_messaging(self):
        # A sends to B
        self.agent_a.send(self.id_b, "Hello B")
        
        # B reads
        msgs = self.agent_b.read()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "Hello B")
        self.assertEqual(msgs[0]["from"], self.id_a)
        
        # B reads again (should be empty/archived)
        msgs_2 = self.agent_b.read()
        self.assertEqual(len(msgs_2), 0)

    def test_public_broadcast(self):
        self.agent_a.send("public", "Announcement")
        
        msgs = self.agent_b.read()
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "Announcement")

if __name__ == '__main__':
    unittest.main()
