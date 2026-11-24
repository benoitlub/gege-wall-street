import unittest
from directional import simulate

class DirectionalTests(unittest.TestCase):
    def test_short_disabled(self):
        self.assertEqual(simulate([100-i for i in range(40)],lambda h:-1)["final"],20)
    def test_short_falling(self):
        self.assertGreater(simulate([100-i for i in range(40)],lambda h:-1,shortable=True)["final"],20)
    def test_short_rising(self):
        self.assertLess(simulate([100+i for i in range(40)],lambda h:-1,shortable=True)["final"],20)
    def test_flat_cost(self):
        self.assertLess(simulate([100]*40,lambda h:1)["final"],20)
