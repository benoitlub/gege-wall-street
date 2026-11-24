import unittest
from octopus_adapter import decode_output
class DecodeTests(unittest.TestCase):
    def test_fenced(self):
        self.assertEqual(decode_output({"text":"Voici:\n```json\n{\"hypotheses\":[]}\n```"}),{"hypotheses":[]})
    def test_direct(self):
        self.assertEqual(decode_output({"hypotheses":[]}),{"hypotheses":[]})
    def test_truncated(self):
        with self.assertRaises(ValueError):
            decode_output({"text":"{\"hypotheses\":["})
