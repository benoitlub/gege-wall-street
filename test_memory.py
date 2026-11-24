import unittest
from memory import summarize

class MemoryTests(unittest.TestCase):
    def test_unknown_is_rejected(self):
        result, history = summarize({"timestamp":"demo","observations":[{"decision":"skip","checks":{}}]}, [])
        self.assertEqual(result["summary"]["rejected"],1)
        self.assertFalse(result["observations"][0]["paper_order"])
        self.assertIn("LP protection unverified (missing or invalid)",result["observations"][0]["guardian_reasons"])
        self.assertIsNone(result["portfolio"]["valuation_eur"])
        self.assertEqual(len(history),1)
    def test_duplicate(self):
        snapshot={"timestamp":"demo","observations":[]}
        _, history=summarize(snapshot,[])
        _, history=summarize(snapshot,history)
        self.assertEqual(len(history),1)

if __name__=="__main__":
    unittest.main()
