from unittest import TestCase
from test_AbstractRunner import ConcreteRunner
from yaw.core.RunnerFactory import RunnerFactory


class TestRunnerFactory(TestCase):
    def test_derive_1(self):
        info = {"type": "type",
                "env_file": ["envA", "envB"]}
        r = ConcreteRunner(**info)
        rr = RunnerFactory().derive(r)

        for i, d in enumerate(rr):
            print(i, d.env_file)
            self.assertEqual(d.env_file, info["env_file"][i])

    def test_derive_2(self):
        info = {"type": "type",
                "env_file": ["envA", "envB"],
                "log_name": ["logA", "logB"]}
        r = ConcreteRunner(**info)

        rr = RunnerFactory().derive(r)
        for i, d in enumerate(rr):
            print(i, d.env_file, d.log_name)
            self.assertEqual(d.env_file, info["env_file"][i])
            self.assertEqual(d.log_name, info["log_name"][i])

    def test_derive_mirror(self):
        info = {"type": "type",
                "env_file": ["envA", "envB"],
                "log_name": ["logA", "logB"], "mirror": 1}
        r = ConcreteRunner(**info)

        rr = RunnerFactory().derive(r)
        for i, d in enumerate(rr):
            print(i, d.env_file, d.log_name)
            self.assertEqual(d.env_file, info["env_file"][i])
            self.assertEqual(d.log_name, info["log_name"][i])

    def test_derive_mirror_real(self):
        info = {"type": "type",
                "env_file": ["envA", "envB"],
                "log_name": ["logA", "logB"], 
                "mirror": 2}
        r = ConcreteRunner(**info)
        rr = RunnerFactory().derive(r)
        self.assertEqual(len(rr), 2*2)

        for i, d in enumerate(rr):
            print(i, d.env_file, d.log_name, "at", id(d))
            self.assertEqual(d.env_file, info["env_file"][i % 2])
            self.assertEqual(d.log_name, info["log_name"][i % 2])
