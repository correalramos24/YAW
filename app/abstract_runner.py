
from pathlib import Path
import os
from dataclasses import dataclass, field, MISSING
from utils import *

@dataclass
class AbstractRunner:
    
    type : str
    rundir: Path
    log_name : str = None
    env_file: Path = None
    dry : bool = False

    required_fields = ["type", "rundir"]
    required_fields_msg = "are required arguments!"

    def __post_init__(self):
            # Expand bash env variables
        for v in self.__dict__.values():
            if isinstance(v, str) and v.startswith("$"):
                #print(">Expanding bash env var", v)
                env_val = os.getenv(v[1:])
                if env_val is None:
                    raise Exception("Unable to find env var", v, env_val)
                else:
                    v = env_val

        self.env_file = Path(self.env_file) if self.env_file else None
        self.rundir = Path(self.rundir) if self.rundir else None

    def manage_parameters(self):
        # Manage log file
        if self.log_name is None:
            print("WARNING: Not using a log, appending all to STDOUT")
        else:
            print(f"Using {self.log_name}, appending STDOUT and STDERR")
        # Manage rundir:
        if not check_path_exists(self.rundir):
            create_dir(self.rundir)
            print(f"Using {self.rundir} as rundir")
        else:
            print(f"WARNING, rundir {self.rundir} already exists!")

    @staticmethod
    def generate_bash_wrapper(fPath : Path, cmds : list[str]):
        cmds_with_endline = '\n'.join(cmds)
        with open(fPath, mode="w") as bash_file:
            bash_file.write(f"""#!/bin/bash
# AUTOMATED BASH WRAPPER GENERATION:
{cmds_with_endline}
            """)
        print(f"Created", fPath)
    def run(self):
        raise Exception("UNDEFINED RUN!")
    



