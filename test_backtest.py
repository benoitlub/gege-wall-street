import unittest
from backtest import simulate, compare

class BacktestTests(unittest.TestCase):
    def test_cash(self):
        self.assertEqual(simulate([1.]*40,lambda h:False)["final"],20)
    def test_costs(self):
        self.assertLess(simulate([1.]*40,lambda h:True)["final"],20)
    def test_causality(self):
        seen=[]
        simulate(list(range(1,41)),lambda h:seen.append(len(h)) or False)
        self.assertEqual(seen,list(range(20,40)))
    def test_compare(self):
        self.assertEqual(len(compare(list(range(1,101)))),5)
