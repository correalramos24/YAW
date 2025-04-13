from .AbstractRunner import AbstractRunner
from utils import *



class VoidRunner(AbstractRunner):
    
    def __init__(self, run_name):
        self.parameters = {
            "recipie_name": run_name
        }
        
        self.runner_result = 0
        self.runner_status = "VOID RUNNER. Check the recipe."

        
    def run(self):
        print("VOID RUNNER. Check the recipe.")
        return 0
    
    def manage_parameters(self):
        return 0
    
    def manage_multi_recipie(self):
        return 0
        
        