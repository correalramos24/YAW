from pathlib import Path
import subprocess, os, re
from .utils_print import *
from .utils_py import *

def expand_bash_env_vars(value:  str|list[str]) -> str|list[str]:
    """Convert the bash variables ($VAR or ${VAR}) to the value.
    """
    if is_a_str(value) and "$" in value:
        log("Expanding bash env var at", value)
        return __expand_env_variables(value)
    if is_a_list(value) and value[0] and "$" in ''.join(value):
        log("Searching bash env vars at", stringfy(value))
        return [__expand_env_variables(val) for val in value]

def __expand_env_variables(line: str) -> str:
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

def execute_script(script: str, args: str|None, rundir: Path, log_file=None):
    if not args: 
        args = ""
        args_str = "without args"
    else:
        args_str = "with " + str(args)

    if not rundir:
        rundir = os.getcwd()

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