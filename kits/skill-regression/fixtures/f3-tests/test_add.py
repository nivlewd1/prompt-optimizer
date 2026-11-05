import unittest
from add import add

class T(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
    def test_neg(self):
        self.assertEqual(add(-1, 1), 0)

if __name__ == "__main__":
    unittest.main()
