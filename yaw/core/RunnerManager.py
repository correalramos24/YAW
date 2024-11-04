from utils import *
from . import AbstractRunner, BashRunner, SlurmRunner, BashRunnerRundir

from pathlib import Path
import yaml, traceback
from itertools import product


class RunnerManager:

    runners: dict = {
        "BashRunner": BashRunner,
        "BashRunnerRundir": BashRunnerRundir,
        "SlurmRunner": SlurmRunner
    }

    def __init__(self, input_files: list[Path], 
        run_step_names : list[str], print_multi : bool
    ):
        self.input_files        : list[Path] = input_files
        self.steps              : list[AbstractRunner|None] = []
        self.step_names         : list[str] = []
        self.print_multi        : bool = print_multi
        self.run_step_name      : list[str] = run_step_names
        self.generic_params     : dict = dict()     # At YAW level
        if self.step_names:
            info("Executing only", stringfy(self.step_names), "step(s)")

    @property
    def runner_params(self) -> set[str]:
        return {param for runner in self.runners.values()
                    for param in runner.get_parameters()}

    @property
    def multi_value_parameters(self) -> set[str]:
        return {
            param for runner in self.runners.values()
            for param in runner.get_multi_value_params()
        }

    # PARSE:
    def parse_files(self) -> None:
        print("=" * 40 + "PARSING" + "=" * 40)
        [self.__parse_file(f) for f in self.input_files]
        print("=" * 87)

    def __parse_file(self, input_file) -> None:
        info("Parsing recipe", input_file)
        recipie_gen_params = self.__get_generic_parameters(input_file)
        with open(input_file, "r") as f:
            content : dict = yaml.safe_load(f)
            # Discard generic parameters:
            content = {param : value for param, value in content.items()
                       if param not in recipie_gen_params.keys()}
            print("-" * 87)
            for step_id, (name, content) in enumerate(content.items()):
                try:
                    #TODO: Add YAW generic parameters
                    content.update(recipie_gen_params)
                    step_t, step_str = content["type"], f"{step_id} - {name}"
                    print(f"Building recipe {step_str} from {input_file}")
                    for variation in self.get_variations(**content):    
                        self.steps.append(self.runners[step_t](**variation))
                        self.step_names.append(name)
                except Exception as e:
                    error(f"While processing recipe {step_str}->", str(e))
                    print("Excluding step", step_id, "with name", name)
                    self.steps.append(None)
                    self.step_names.append(name)
                print("-" * 87)

    def __get_generic_parameters(self, recipie_file: Path) -> dict:
        info(f"Searching for generic parameters @ {recipie_file}...")
        info(f"Using {self.runner_params} to search parameters...")
        ret = {}
        with open(recipie_file, "r") as f:
            content : dict = yaml.safe_load(f)
            param_names = set(content.keys())
            generic_params = self.runner_params & param_names
            ret = {param: content[param] for param in generic_params}
        if len(ret):
            print(f"Generic parameters @ {recipie_file}: {ret}")
        else:
            print(f"Generic parameters @ {recipie_file}: None")
        return ret
          
    def get_variations(self, **params):
        if self.__is_a_multi_recipie(**params):
            info("Deriving multi-parameter...")
            return self.__derive_multi_recipe(self.print_multi, **params)
        else:
            return [params]

    def __is_a_multi_recipie(self, **params) -> bool:
        return len([
            param for param, val in params.items()
            if is_a_list(val) and not "__" in param and
            not param in self.multi_value_parameters
        ]) >= 1

    def __derive_multi_recipe(self, print_combs: bool, **params) -> list[dict]:
        
        # 1. GET MULTI-PARAMETERS 
        multi_params = [ (param, val) for param, val in params.items()
                        if is_a_list(val) and not "__" in str(param) and
                        not param in self.multi_value_parameters
        ]

        # 2. CHECK MODE FOR VARIATION GENERATION:
        multi_param_str= ' '.join(param for param, _ in multi_params)
        if safe_check_key_dict(params, "mode") == "cartesian":
            join_op = product
            print("Cartesian mode for multi-parameter(s):", multi_param_str)
        else: # ZIP MODE -> DEFAULT
            join_op = zip
            print("Using zip mode for multi-parameter(s):", multi_param_str)
            # Check params len: all multi-params needs to be the same!
            b_length = [
                len(params[param]) == len(params[multi_params[0][0]])
                for param, _ in multi_params
            ]

            if not all(b_length):
                critical("Invalid size for multi-parameters",
                         str([len(params[param]) for param, _ in multi_params]))

        # 3. GENERATE COMBINATIONS
        variation_params = [param for param, _ in multi_params]
        unique_params = {
            param: value for param, value in params.items() 
            if param not in variation_params
        }
        variations_values = list(
            join_op(*[params[param] for param, _ in multi_params])
        )
        variations = [
            {**unique_params, **dict(zip(variation_params, variation))}
            for variation in variations_values
        ]
        info(f"Found {len(variations)} multi-params combinations")

        if print_combs:
            print("# Unique parameters:")
            print('\n'.join(f"{param}: {val}" for param, val in unique_params.items()))

            print("# Combinations:")
            for i_comb, variation in enumerate(variations):
                print(i_comb, variation)
        return variations

    # RUN:
    def run_steps(self):
        if self.run_step_name:
            print("Only executting steps with name", stringfy(self.run_step_name))
        else:
            self.run_step_name = self.step_names
        print("=" * 40 + "RUNNING" + "=" * 40)
        for i, (name, step) in enumerate(zip(self.step_names, self.steps)):
            if step and name in self.run_step_name:
                try:
                    print(f"Checking step {i} ({name})")
                    step.manage_parameters()
                except Exception as e:
                    error(f"While checking recipe {i} ->", str(e))
                    traceback.print_exception(e)
                try:
                    print(f"Executing step {i} ({name})")
                    step.run()
                except Exception as e:
                    error(f"While executing recipe {i} ->", str(e))
                    traceback.print_exception(e)
            elif step and name not in self.run_step_name :
                print(f"Recipie {i} - {name} skipped due cmd line")
            else:
                print(f"Recipe {i} - {name} is empty, check recipie -> SKIP")
            print("-" * 87)
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


