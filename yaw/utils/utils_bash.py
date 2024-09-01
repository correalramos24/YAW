from pathlib import Path
import subprocess
import os
import re
from .utils_print import *


def expand_env_variables(line: str) -> str:
    pattern = r'\$(\w+)|\$\{(\w+)\}'
    def replace_variable(match):
        var_name = match.group(1) or match.group(2)
        value = os.getenv(var_name)
        if not value:
            raise Exception("Unable to find env var", var_name)
        else:
            return value

    # Substitute variables in the string with their values
    return re.sub(pattern, replace_variable, line)

def generate_bash_script(f_path: Path, cmds : list[str]):
    cmds_with_end_line = '\n'.join(cmds)
    with open(f_path, mode="w") as bash_file:
        bash_file.write(f"""#!/bin/bash
# AUTOMATED BASH WRAPPER GENERATION:
{cmds_with_end_line}
""")
        log(f"Created", f_path)

def execute_script(script, args, rundir, log_file=None):
    if not args: 
        args = ""
        args_str = "without args"
    else: 
        args_str = "with " + args
    if log_file:
        info(f"Executing {script} {args_str} at {rundir}, writing STDOUT to {log_file}")
        file_desc = open(log_file, mode="w")
    else:
        info(f"Executing {script} {args_str} at {rundir}")
        file_desc = None

    r = subprocess.run(f"/bin/bash {script} {args}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT, stdout=file_desc)

    if log_file is not None:
        file_desc.close()

    info(f"Completed {script} with return code: ", r.returncode)

def execute_command(cmd: str, rundir: Path):
    subprocess.run(f"{cmd}", cwd=rundir,
            shell=True, text=True,
           stderr=subprocess.STDOUT)