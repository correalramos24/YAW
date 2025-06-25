from .AbstractRunner import AbstractRunner
from utils import *



class VoidRunner(AbstractRunner):
    
    def __init__(self, run_name, error_msg : str):
        self.parameters = {
            "recipie_name": run_name
        }
        
        self.runner_result = 0
        self.runner_status = error_msg

    def run(self):
        print("VOID RUNNER. Check the recipe.")
        raise Exception(f"VOID RUNNER. Check input recipie")
        return 0
    
    def manage_parameters(self):
        raise Exception(f"VOID RUNNER. Check input recipie")
    
    def manage_multi_recipie(self):
        return 0
        
    def is_a_multirecipie(self):
        return False