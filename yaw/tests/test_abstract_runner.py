import unittest
from yaw.core.BashRunner import BashRunner
from pathlib import Path
class TestAbstractRunner(unittest.TestCase):

    def setUp(self):
        # Initialize any necessary objects or state before each test
        self.test_dir = Path("tests/test_dir")
        self.runner = BashRunner(type="BashRunner", bash_cmd="ls", rundir=self.test_dir)

    def test_initialization(self):
        # Test the initialization of the AbstractRunner
        self.assertIsInstance(self.runner, BashRunner)

    def test_some_method(self):
        # Test some method of AbstractRunner
        self.assertEqual(22, 22)

    def tearDown(self):
        # Clean up any necessary objects or state after each test
        pass

if __name__ == '__main__':
    print("Running tests for AbstractRunner...")
    unittest.main()