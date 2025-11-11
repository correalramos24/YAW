from unittest import TestCase
from yaw.core.AbstractRunner2 import AbstractRunner2

class TestAbstractRunner2(TestCase):

    def test_req_args_not_set(self):
        with self.assertRaises(Exception):
            ar = AbstractRunner2()
            print(ar)

    def test_simple(self):
        ar = AbstractRunner2(type="simple")
        print(ar)