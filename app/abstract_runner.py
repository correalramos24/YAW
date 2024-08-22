
from pathlib import Path
import os
from dataclasses import dataclass

@dataclass
class AbstractRunner:
    
    type : str

    @staticmethod
    def empty_recipe():
        pass

    def __post_init__(self):
        for v in self.__dict__.values():
            if isinstance(v, str) and v.startswith("$"):
                print(">Expanding bash env var", v)
                env_val = os.getenv(v[1:])
                if env_val is None:
                    raise Exception("Unable to find env var", v, env_val)
                else:
                    v = env_val

    def manage_parameters(self):
        raise Exception("UNDEFINED RUN")

    def run(self):
        raise Exception("UNDEFINED RUN!")
    



