
from pathlib import Path



class AbstractRunner:
    
    @staticmethod
    def empty_recipe():
        pass

    def check_parameters(self):
        raise Exception("UNDEFINED RUN")

    def run(self):
        raise Exception("UNDEFINED RUN!")
    



