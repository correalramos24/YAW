from .AbstractRunner import AbstractRunner
from utils import *

class VoidRunner(AbstractRunner):

    def __init__(self, run_name, error_msg : str):
        self.recipie_name = run_name
        self.runner_result = 0
        self.runner_status = error_msg

    def check_parameters(self):
        raise Exception(f"VOID RUNNER. Check input recipie")
        return 0

    def run(self):
        self._err(f"VOID RUNNER. Check input recipie")
        return 0

    def manage_parameters(self):
        raise Exception(f"VOID RUNNER. Check input recipie")

    #def get_result(self):
    #    return "VOID Runner #> Check input recipie(s)"

    def is_a_multirecipie(self):
        return False
