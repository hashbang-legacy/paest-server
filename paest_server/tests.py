""" Unit tests for various classes in paest_server """

import unittest
import base58

class TestBase58(unittest.TestCase):
    """ Tests for base58.py """

    def test_length(self):
        """ Test various lengths of output from random58 """
        # Negative returns empty string
        self.assertEqual(0, len(base58.random58(-1)))

        # Zero returns empty string
        self.assertEqual(0, len(base58.random58(0)))

        # Paest Id 
        self.assertEqual(4, len(base58.random58(4)))

        # Paest Keu
        self.assertEqual(20, len(base58.random58(20)))

def main():
    """ Launch unittest's main """
    unittest.main()

if __name__ == "__main__":
    main()
