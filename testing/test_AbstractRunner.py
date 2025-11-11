from unittest import TestCase

from utils import LoggerLevels
from yaw.core.AbstractRunner import AbstractRunner
from utils.utils_print import MyLogger
import os

class ConcreteRunner(AbstractRunner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("Testing...")

class TestAbstractRunner(TestCase):
    MyLogger.set_verbose_level(LoggerLevels.DEBUG)

    def test_init(self):
        r = ConcreteRunner(** {"type":"type"})
        print(r)

    def test_bad_parmeters(self):
        with self.assertRaises(TypeError) as exception:
            r = ConcreteRunner(**{"type":"test-type","alfa": "beta"})
        print("Succesfully failed:", exception.exception)

    def test_missing_req_args(self):
        with self.assertRaises(TypeError) as exception:
            r = ConcreteRunner(**{"recipie_name" : "test-recipie-name"})
        print("Succesfully failed:", exception.exception)

    def test_expand_bash_vars(self):
        os.environ["YAW_TEST_VAR"] = "test"
        os.environ["YAW_OTHER_TEST_VAR"] = "test33"
        info = {
            "type": "test-type", "rundir" : "$YAW_TEST_VAR",
            "recipie_name" : "test-recipie-name-$YAW_OTHER_TEST_VAR",
            "env_file" : "$YAW_TEST_VAR"
        }
        r = ConcreteRunner(**info)
        r.check_parameters()
        self.assertEqual(r.rundir, "test")
        self.assertEqual(r.recipie_name, "test-recipie-name-test33")
        self.assertEqual(r.env_file, "test")

    def test_expand_yaw_vars(self):
        os.environ["YAW_TEST_VAR"] = "test"
        info = {
            "type": "test-type", "rundir": "$YAW_TEST_VAR",
            "recipie_name": "name",
            "track_env" : "&recipie_name&.env",
            "log_name": "&recipie_name&.log",
        }
        r = ConcreteRunner(**info)
        r.check_parameters()
        self.assertEqual(r.rundir, "test")
        self.assertEqual(r.track_env, "name.env")
        self.assertEqual(r.log_name, "name.log")

    def test_derive_recipie(self):
        pass

    def test_manage_parameters(self):
        pass