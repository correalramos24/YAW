from utils import *
from . import AbstractRunner, BashRunner
from . import VoidRunner, BashSlurmRunner
from nemo import NEMO5Runner, TestNEMO5Runner,NEMO5XIOSRunner

from pathlib import Path
import traceback


class RunnerManager(metaAbstractClass):

    runners: dict = {   
        "BashRunner": BashRunner,
        "BashSlurmRunner": BashSlurmRunner,
        "NEMO5Runner": NEMO5Runner,
        "NEMO5XIOSRunner": NEMO5XIOSRunner,
        "TestNEMO5Runner": TestNEMO5Runner,
    }

    def __init__(self, input_files: list[Path], run_step_names : list[str]):
        self.input_files        : list[Path] = input_files
        self.steps              : list[AbstractRunner|None] = []
        self.steps_derived      : list[AbstractRunner|None] = []
        self.tr_steps           : list[str] = run_step_names
        self.generic_params     : dict = dict()     # At YAW level
    
    # PARSE:
    def parse_files(self) -> None:
        """
        Parse all the input recipies
        """
        [self.__parse_file(f) for f in self.input_files]

    def __parse_file(self, input_file) -> None:
        """
        Parse a recepie file from input_file.
        """
        info("Parsing recipe", input_file)
        with open(input_file, "r") as yaml_file:
            #1. Get generic parameters for all the recipies on the file:
            all_recipies_content = get_yaml_content(yaml_file)
            generic = intersect_dict_keys(all_recipies_content, self.__params())
            self._info("Generic parameters found:", generic)
            #2. Remove the generic parameters to don't parse them:
            content = remove_keys(all_recipies_content, self.__params())            
            print("*" * 87)
            #3. Loop all the recipie parameters
            for name, content in content.items():
                print(f"Parsing recipe {name} from {input_file}")
                try:
                    content.update(generic) 
                    content["recipie_name"] = name
                    step_type = content["type"]
                    self.steps.append(self.runners[step_type](**content))
                except Exception as e:
                    self._err(f"While parsing recipe {name}->", str(e))
                    self._err("=> Excluding step with name", name)
                    self.steps.append(VoidRunner(name, str(e)))
                print("-" * 87)

    # DERIVE:
    def derive_recipies(self):
        for recipie in self.steps:
            #TODO: This can raise an exception...
            self.steps_derived.extend(recipie.derive_recipies())
                
    # RUN:
    def run_steps(self):
        if self.tr_steps:
            print("Only executing steps with name", stringfy(self.tr_steps))
        
        for i, step in enumerate(self.steps_derived):
            name = step.get_recipie_name()
            if self.tr_steps and not any(n in name for n in self.tr_steps):
                info(f"Recipie {i} - {name} skipped due cmd line")
                step.set_result(0, "skipped due cmd line --steps")
                continue
            try:
                self._info(f"Managing parameters @ step {i} ({name})")
                step.manage_parameters()
                self._ok("DONE")
            except Exception as e:
                self._err(f"{name}->", str(e))
                step.set_result(-1, "Error checking recipie!")
                #self._log(traceback.format_exc())
                continue
            try:
                self._info(f"Executing step {i} ({name})")
                step.run()
                self._ok("DONE")
            except Exception as e:
                self._err(f"While executing recipe {i} ->", str(e))
                step.set_result(-1, f"{str(e)}")
            print("-" * 87)
        
    # PRINT:
    def print_results(self):
        for i, step in enumerate(self.steps_derived):
            if step is None:
                print(f"Step {i}: Undefined")
            else:
                print(f"Step {i}: {step.get_result()}")
    
    # GENERATION:
    @classmethod
    def generate_template(cls, runner_name):
        if not runner_name in cls.runners:
            cls._err(f"Not found {runner_name}, unable to generate template")
            exit(1)
        else:
            cls.runners[runner_name].generate_yaml_template()

    @classmethod
    def get_runners(cls) -> list[str]:
        return [str(k) for k in cls.runners.keys()]

    #================================PRIVATE METHODS============================
    def __params(self) -> set[str]:
        """
        Gather all the parameters used by the runners, as they 
        are reserved names (cannot be used for recipie names)
        """
        aux = list(self.runners.values()) + [AbstractRunner]
        return {param for runner in aux for param in runner.get_parameters()}
    