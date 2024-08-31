from utils import *
from . import SlurmRunner, AbstractRunner
from .BashRunner import BashRunner
from pathlib import Path
import yaml
import traceback
from itertools import product, combinations


class RunnerManager:

    runners: dict = {
        "BashRunner": BashRunner,
        "SlurmRunner": SlurmRunner
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
                    if RunnerManager._is_a_multi_recipie(step_t, **content):
                        variations = RunnerManager._derive_multi_recipe(name, step_t, True, **content)
                        for variation in variations:
                            self.steps.append(self.runners[step_t](**variation))
                    else:
                        self.steps.append(self.runners[step_t](**content))
                except Exception as e:
                    error(f"While processing recipe {step_str}->", str(e))
                    traceback.print_exc()
                    print("Excluding step", step_id, "with name", name)
                    self.steps.append(None)
                print("-" * 87)

    @staticmethod
    def _is_a_multi_recipie(step_type : str, **params) -> bool:
        multi_value = RunnerManager.runners[step_type].get_multi_value_params()
        return len([
            param for param, val in params.items()
            if is_a_list(val) and not "__" in param and
            not param in multi_value
        ]) >= 1

    @staticmethod
    def _derive_multi_recipe(step_name: str, step_type : str, print_combs: bool, **params) -> list[dict]:
        info("Deriving multi-parameter for step", step_name)
        # 1. GET MULTI-PARAMETERS
        multi_value = RunnerManager.runners[step_type].get_multi_value_params()
        multi_params = [ (param, val) for param, val in params.items()
                        if is_a_list(val) and not "__" in str(param) and
                        not param in multi_value
        ]

        # 2. CHECK MODE FOR VARIATION GENERATION:
        if safe_check_key_dict(params, "mode"):
            # 2A. CARTESIAN
            join_op = product
            info("Cartesian mode for multi-parameter(s):", ' '.join(param for param, _ in multi_params))
        else:
            # 2B. ZIP MODE
            join_op = zip
            info("Using zip mode for multi-parameter(s):", ' '.join(param for param, _ in multi_params))
            # Check params len: all multi-params needs to be the same!
            b_lens = [
                len(params[param]) == len(params[multi_params[0][0]])
                for param, value in multi_params
            ]

            if not all(b_lens):
                critical("Invalid size for multi-parameters",
                         str([len(params[param]) for param, _ in multi_params]))

        # 3. GENERATE COMBINATIONS
        variation_params = [param for param, _ in multi_params]
        unique_params = {
            param: value for param, value in params.items() if param not in variation_params
        }
        variations_values = list(join_op(*[params[param] for param, _ in multi_params]))
        variations = []
        for variation in variations_values:
            aux = {"root_step": step_name, **unique_params}
            variation_rundir = '_'.join(stringfy(value) for value in variation)
            for param, value in zip(variation_params, variation):
                aux[param] = value
            aux["rundir"] = variation_rundir
            variations.append(aux)

        print(f"Requested {len(variations)} executions with multi-params combinations")

        if print_combs:
            print("# Unique parameters:")
            print('\n'.join(f"{param}: {val}" for param, val in unique_params.items()))

            print("# Combinations:")
            for i_comb, variation in enumerate(variations):
                print(i_comb, variation)
        return variations

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
                error(f"While executing recipe {i} ->", str(e))
                print(traceback.format_exc())
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


