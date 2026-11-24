import unittest
from decimal import Decimal
from treasury import Treasury

class TreasuryTests(unittest.TestCase):
    def test_profit_split(self):
        t=Treasury()
        t.settle(4)
        self.assertEqual(t.capital,Decimal("22"))
        self.assertEqual(t.reserve,Decimal("1"))
        self.assertEqual(t.paper_payout(),Decimal("1"))
    def test_loss_recovery(self):
        t=Treasury()
        t.settle(4)
        t.settle(-2)
        self.assertEqual(t.paper_payout(),0)
        t.settle(2)
        self.assertEqual(t.deficit,0)
        self.assertEqual(t.paper_payout(),Decimal("1"))
        self.assertEqual(t.capital+t.reserve+t.paid,Decimal("24"))
    def test_no_overdraft(self):
        t=Treasury()
        with self.assertRaises(ValueError): t.settle(-21)
