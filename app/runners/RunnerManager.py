from app.utils import *
from . import slurmRunner, nemoRunner, AbstractRunner
from .BashRunner import BashRunner
from pathlib import Path
import yaml
import traceback

class RunnerManager:

    runners: dict = {
        "BashRunner": BashRunner,
        "SlurmRunner": slurmRunner,
        "NemoRunner": nemoRunner,
    }

    def __init__(self, input_files: list[Path]):
        self.input_files = input_files
        self.steps : list[AbstractRunner|None] = []

    # PARSE:
    def parse_files(self):
        print("=" * 40 + "PARSING" + "=" * 40)
        [self._parse_file(f) for f in self.input_files]
        print("=" * 87)

    def _parse_file(self, input_file) -> None:
        print("Parsing recipe", input_file)
        with open(input_file, "r") as f:
            content : dict = yaml.safe_load(f)
            for step_id, (name, content) in enumerate(content.items()):
                step_t = content["type"]
                step_str = f"{step_id} ({step_t} - {name})"
                print(f"Building recipe {step_str} from {input_file}")
                try:
                    if RunnerManager._is_a_multi_recipie(**content):
                        variations = RunnerManager._derive_multi_recipe(**content)
                    else:
                        self.steps.append(self.runners[step_t](**content))
                except Exception as e:
                    error(f"While processing recipe {step_str}->", str(e))
                    print("Excluding step", step_id, "with name", name)
                    self.steps.append(None)
                print("-" * 87)

    @staticmethod
    def _is_a_multi_recipie(**params) -> bool:
        return len([
            param for param, val in params.items()
            if is_a_list(val) and not "__" in str(param)
        ]) > 1

    def _derive_multi_recipe(**params) -> bool:
        return True

    # RUN:
    def run_steps(self):
        print("=" * 40 + "RUNNING" + "=" * 40)
        for i, step in enumerate(self.steps):
            try:
                print(f"Executing step {i}")
                if step:
                    step.manage_parameters()
                    step.run()
                else:
                    print(f"Recipe {i} is empty, check the parsing step -> SKIP")
            except Exception as e:
                warning(f"While executing recipe {i} ->", str(e))
        print("=" * 87)

    # GENERATION:
    @classmethod
    def generate_template(cls, runner_name):
        if not runner_name in cls.runners:
            raise Exception("Bad runner type", runner_name)
        else:
            cls.runners[runner_name].generate_yaml_template()
    @classmethod
    def get_runners(cls) -> list[str]:
        return [str(k) for k in cls.runners.keys()]


if __name__ == "__main__":
    print("A")