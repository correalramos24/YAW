
from pathlib import Path
import os
from dataclasses import dataclass
from utils import *

@dataclass
class AbstractRunner:
    
    type : str = None
    rundir: Path = None
    log_name : str = None
    env_file: Path = None
    dry : bool = False

    required_fields = ["type", "rundir"]
    required_fields_msg = ", ".join(required_fields) + "are required arguments!"
    delim = "#"*33 + "-YAW-" + "#"*33

    help_dict = {
        "type" : "Type of runner",
        "rundir" : "Rundir path to execute the runner.",
        "log_name" : "Log file to dump the STDOUT and STDERR",
        "env_file" : "Environment file to use",
        "dry" : "Dry run, only generate running directory"
    }

    def __post_init__(self):
            # Expand bash env variables
        for field, value in self.__dict__.items():
            
            if isinstance(value, str) and "$" in value:
                info("Expanding bash env var at", value)
                self.__dict__[field] = expand_env_variables(value)

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
    
    @classmethod
    def __generate_yaml_template_content(cls):
        ret = ""
        for parameter, comment in cls.help_dict.items():
            if parameter == "type":
                ret += f"  {parameter}: {cls.type}\n"
            else:
                ret += f"  {parameter}: #{comment}\n"
        return ret

    @classmethod
    def generate_yaml_template(cls):
        ret = f"{AbstractRunner.delim}\n## TEMPLATE FOR {cls.type} RUNNER\n"
        ret += "your_recipe_name:\n"
        ret += cls.__generate_yaml_template_content()
        ret += AbstractRunner.delim + '\n'

        with open(cls.type+".yaml", mode="w") as template:
            template.write(ret)



