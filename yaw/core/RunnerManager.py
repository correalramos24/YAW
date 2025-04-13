from utils import *
from . import AbstractRunner, BashRunner, SlurmRunner, BashRunnerRundir
from . import VoidRunner

from pathlib import Path
import traceback
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
        self.print_multi        : bool = print_multi
        self.run_step_name      : list[str] = run_step_names
        self.generic_params     : dict = dict()     # At YAW level
        if self.run_step_name:
            info("Executing only", stringfy(self.run_step_name), "step(s)")
    
    def runner_params(self) -> set[str]:
        aux = list(self.runners.values()) + [AbstractRunner]
        return {param for runner in aux for param in runner.get_parameters()}
    
    def multi_value_parameters(self) -> set[str]:
        return {
            param for runner in self.runners.values()
            for param in runner.get_multi_value_params()
        }

    # PARSE:
    def parse_files(self) -> None:
        """
        Parse all the input recipies
        """
        print("=" * 40 + "PARSING" + "=" * 40)
        [self.__parse_file(f) for f in self.input_files]
        print("=" * 87)

    def __parse_file(self, input_file) -> None:
        """
        Parse a recepie file from input_file.
        """
        info("Parsing recipe", input_file)
        with open(input_file, "r") as yaml_file:
            all_recipies_content = get_yaml_content(yaml_file)
            generic = intersect_dict_keys(all_recipies_content, self.runner_params())
            content = remove_keys(all_recipies_content, self.runner_params())
            info2("Generic parameters found:", generic)
            print("=" * 87)
            for step_id, (name, content) in enumerate(content.items()):
                step_str = f"{step_id}-{name}"
                print(f"Building recipe {step_str} from {input_file}")
                try:
                    content.update(generic)
                    step_type = content["type"]
                    for var_id, variation in enumerate(self.get_variations(**content)):
                        variation["recipie_name"] = name+f"_{var_id}"
                        self.steps.append(self.runners[step_type](**variation))
                except Exception as e:
                    error(f"While parsing recipe {step_str}->", str(e))
                    print("=> Excluding step with name", step_str)
                    self.steps.append(VoidRunner(step_str))
                    self.steps[-1].set_result(-1, f"Error parsing recipe ({str(e)})")
                print("-" * 87)

    def get_variations(self, **params):
        if self.__is_a_multi_recipie(**params):
            info("Deriving multi-parameter...")
            return self.__derive_multi_recipe(**params)
        else:
            return [params]

    def __is_a_multi_recipie(self, **params) -> bool:
        return len([
            param for param, val in params.items()
            if is_a_list(val) and not "__" in param and
            not param in self.multi_value_parameters()
        ]) >= 1

    def __derive_multi_recipe(self, **params) -> list[dict]:
        # 1. GET MULTI-PARAMETERS 
        multi_params = [ (param, val) for param, val in params.items()
                        if is_a_list(val) and not "__" in str(param) and
                        not param in self.multi_value_parameters()
        ]

        # 2. CHECK MODE FOR VARIATION GENERATION:
        multi_param_names=[param for param, _ in multi_params]
        multi_param_str= ' '.join(multi_param_names)
        join_mode = params.get("mode", "zip")

        if join_mode == "cartesian":
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
            {**unique_params, **dict(zip(variation_params, variation)),
             "multi_params": multi_param_names}
            for variation in variations_values
        ]
        info(f"Found {len(variations)} multi-params combinations")

        if self.print_multi:
            print("# Unique parameters:")
            print('\n'.join(f"{param}: {val}" for param, val in unique_params.items()))

            print("# Combinations:")
            for i_comb, variation in enumerate(variations):
                print(i_comb, variation)
        return variations

    # RUN:
    def run_steps(self):
        print("=" * 40 + "RUNNING" + "=" * 40)
        if self.run_step_name:
            print("Only executting steps with name", stringfy(self.run_step_name))
        
        for i, step in enumerate(self.steps):
            if step.is_runable():
                name = step.recipie_name()
                if self.run_step_name and name not in self.run_step_name: 
                    info(f"Recipie {i} - {name} skipped due cmd line")
                    step.set_result(0, "skipped due cmd line --steps")
                    continue
                # A) MANAGE PARAMETERS
                try:
                    step.manage_parameters()
                except Exception as e:
                    error(f"While checking recipe {i} ->", str(e))
                    step.set_result(-1, "Error checking recipie!")
                    continue
                # B) EXECUTE STEP
                try:
                    print(f"Executing step {i} ({name})")
                    step.run()
                except Exception as e:
                    error(f"While executing recipe {i} ->", str(e))
                    step.set_result(-1, "YAW internal error ({str(e)})")
                print("-" * 87)
            else:
                info(f"Recipe {i} is empty, check recipie -> SKIP")
                
        print("=" * 87)

        print("=" * 40 + "RESULTS" + "=" * 40)
        for i, step in enumerate(self.steps):
            if step is None:
                print(f"Step {i}: Undefined")
            else:
                print(f"Step {i}: {step.get_result()}")
        
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

