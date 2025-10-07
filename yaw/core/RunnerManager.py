
from utils import *
from yaw.core import AbstractRunner, BashRunner
from yaw.core import VoidRunner, BashSlurmRunner
from yaw.nemo import NEMO5Runner, TestNEMO5Runner, NEMO5XIOSRunner

from pathlib import Path
from typing import Iterable
# import traceback

class RunnerManager(metaAbstractClass):
    runners: dict = {
        "BashRunner": BashRunner,"BashSlurmRunner": BashSlurmRunner,
        "NEMO5Runner": NEMO5Runner,"NEMO5XIOSRunner": NEMO5XIOSRunner,
        "TestNEMO5Runner": TestNEMO5Runner
    }

    def __init__(self, input_files: list[Path], run_step_names: list[str]):
        self.input_files: list[Path] = input_files
        self.steps: list[AbstractRunner | None] = []
        self.steps_derived: list[AbstractRunner | None] = []
        self.tr_steps: list[str] = run_step_names
        self.generic_params: dict = dict()  # At YAW level

    # ============================PARSE=========================================
    def parse_files(self) -> None:
        """Parse all the input recipies"""
        [self.__parse_file(f) for f in self.input_files]

    def __parse_file(self, input_file) -> None:
        """Parse a recepie file from input_file."""
        print(f"Parsing {input_file}...")
        with open(input_file, "r") as yaml_file:
            # 1. Get generic parameters for all the recipies on the file:
            all_recipies_content = get_yaml_content(yaml_file)
            generic = inter_dict_keys(all_recipies_content, self.__params())
            self._log("Generic parameters found:", generic)
            # 2. Remove the generic parameters to don't parse them:
            content = remove_keys(all_recipies_content, self.__params())
            for r_name, r_params in content.items():
                print(f"Parsing {r_name} recipie")
                try:
                    r_params.update(generic)
                    r_params["recipie_name"] = r_name
                    step_type = r_params["type"]
                    self.steps.append(self.runners[step_type](**r_params))
                except Exception as e:
                    self._err(f"Excluding step {r_name} from {r_name}")
                    self.steps.append(VoidRunner(r_name, str(e)))
        if(len(self.steps) == 0):
            raise Exception("No steps found to derive recipies")

    # ============================DERIVE========================================
    def derive_recipies(self):
        if len(self.steps) == 0:
            self._warn("No steps found to derive recipies")
            return
        for recipie in self.steps:
            # TODO: This can raise an exception...
            self.steps_derived.extend(recipie.derive_recipies())

    # =============================RUN==========================================
    def run_steps(self):
        if self.tr_steps:
            print("Only executing steps with name", stringfy(self.tr_steps))

        for i, step in enumerate(self.steps_derived):
            name = step.get_recipie_name()
            if self.tr_steps and not any(n in name for n in self.tr_steps):
                self._info(f"Recipie {i} - {name} skipped due cmd line")
                step.set_result(0, "skipped due cmd line --steps")
                continue
            try:
                print(f"Checking parameters @ step {i} ({name})")
                step.check_parameters()
            except Exception as e:
                self._err(f"{name}->", str(e))
                step.set_result(-1, "Error checking recipie!")
                # self._log(traceback.format_exc())
                continue
            try:
                print(f"Managing parameters @ step {i} ({name})")
                step.manage_parameters()
                self._ok("MANAGEMENT DONE")
            except Exception as e:
                self._err(f"{name}->", str(e))
                step.set_result(-1, "Error checking recipie!")
                # self._log(traceback.format_exc())
                continue
            try:
                print(f"Executing @ step {i} ({name})")
                step.run()
                self._ok("EXECUTION DONE")
            except Exception as e:
                self._err(f"While executing recipe {i} ->", str(e))
                step.set_result(-1, f"{str(e)}")
            print("-" * 87)

    # =========================PRINT============================================
    def print_results(self):
        for i, step in enumerate(self.steps_derived):
            if step is None:
                print(f"Step {i}: Undefined")
            else:
                print(f"Step {i}: {step.get_result()}")

    # =========================GENERATION=======================================
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

    # ========================PRIVATE METHODS===================================
    def __params(self) -> Iterable[str]:
        """
        Gather all the parameters used by the runners, as they
        are reserved names (cannot be used for recipie names)
        """
        aux = list(self.runners.values()) + [AbstractRunner]
        return {param for runner in aux for param in runner.get_parameters()}
