import unittest
from darwin import rank
class DarwinTests(unittest.TestCase):
    def test_risky_winner_rejected(self):
        self.assertEqual(rank({"risky":{"net_return":2,"max_drawdown":.5,"executions":20}})["next_candidate"],"cash")
    def test_candidate(self):
        self.assertEqual(rank({"steady":{"net_return":.3,"max_drawdown":.05,"executions":20}})["next_candidate"],"steady")
