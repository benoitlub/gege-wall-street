import unittest
from forward import step
from treasury import Treasury

class ForwardTests(unittest.TestCase):
    def test_pair_and_capital(self):
        s={"treasury":Treasury().snapshot(),"events":[]}
        step(s,100,100,1,"SOLEUR")
        self.assertEqual(s["position"]["budget"],5)
        with self.assertRaises(ValueError): step(s,200,100,1,"ETHEUR")
        step(s,200,110,1,"SOLEUR")
        self.assertIsNone(s["position"])
        self.assertEqual(s["events"][-1]["pair"],"SOLEUR")
        self.assertGreater(float(s["treasury"]["capital"]),20)
        step(s,200,110,1,"SOLEUR")
        self.assertEqual(len(s["events"]),2)
