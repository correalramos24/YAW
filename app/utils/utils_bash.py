from pathlib import Path
import subprocess
import os
import re


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

def generate_bash_script(fPath: Path, cmds : list[str]):
    cmds_with_endline = '\n'.join(cmds)
    with open(fPath, mode="w") as bash_file:
        bash_file.write(f"""#!/bin/bash
# AUTOMATED BASH WRAPPER GENERATION:
{cmds_with_endline}
""")
        print(f"Created", fPath)

def execute_script(script, args, rundir, log_file=None):
    if log_file is not None:
        print(f"Executing {script} with {args} at {rundir}, writting STDOUT to {log_file}")
        fdesc_stdout = open(log_file, mode="w") 
    else:
        print(f"Executing {script} with {args} at {rundir}")
        fdesc_stdout = None

    r = subprocess.run(f"/bin/bash {script} {args}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT, stdout=fdesc_stdout)

    if log_file is not None:
        fdesc_stdout.close()

    print("Completed with return code: ", r.returncode)

def execute_command(cmd: str, rundir: Path):
    subprocess.run(f"/bin/bash {cmd}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT)