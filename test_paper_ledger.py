import tempfile
import unittest
from pathlib import Path
from paper_ledger import Ledger

class LedgerTests(unittest.TestCase):
    def test_replay(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ledger.json"
            l=Ledger(p)
            self.assertTrue(l.settle("closed-1",4))
            self.assertTrue(l.payout("pay-1"))
            l=Ledger(p)
            self.assertFalse(l.settle("closed-1",4))
            self.assertFalse(l.payout("pay-1"))
            self.assertEqual(str(l.treasury.paid),"1.00")
            with self.assertRaises(ValueError): l.settle("closed-1",5)
