import unittest
from decimal import Decimal
from guardian import budget,daily_block,token_gate

class GuardianTests(unittest.TestCase):
    def test_budget(self):
        self.assertEqual(budget(Decimal("20")),Decimal(".40"))
    def test_daily_cap(self):
        events=[{"action":"close","timestamp":100,"net":"-1.00"}]
        self.assertTrue(daily_block(events,200))
        self.assertFalse(daily_block(events,90000))
    def test_unknown_fails(self):
        self.assertFalse(token_gate({"eligible":True,"checks":{"lp_verified":True}}))
        self.assertFalse(token_gate({}))
