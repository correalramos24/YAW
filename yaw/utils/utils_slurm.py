
from pathlib import Path
from .utils_print import *
from pathlib import Path
import subprocess
from .utils_print import *

slurm_syntax = {
    "nodes" : "-N", "mpi" : "--ntasks-per-node", "cpus" : "-c",
    "account": "-A", "queue" : "--qos", "time_limit" : "--time",
    "wait" : "-W","contiguous" : "--contiguous",
    "workdir" : "-D"
}

def generate_slurm_script(f_path: Path,
                          slurm_directives : dict[str, any],
                          cmds : list[str], log_file: str):
    formatted_directives = ""
    for directive, val in slurm_directives.items():
        aux = directive.replace("slurm_","")
        if isinstance(val, bool):
            val = ""
        formatted_directives += f"#SBATCH {slurm_syntax[aux]} {val}\n"
    if log_file:
        formatted_directives += f"#SBATCH --output {log_file}"
    cmds_with_end_line = '\n'.join(cmds)
    with open(f_path, mode="w") as bash_file:
        bash_file.write(f"""#!/bin/bash
{formatted_directives}
# {"="*80}
# AUTOMATED SLURM SCRIPT WRAPPER GENERATION:\n
{cmds_with_end_line}
# {"="*80}
""")
        log(f"Created", f_path)

def execute_slurm_script(script, args, rundir):
    if args:
        args_str = "with " + args
    else: 
        args = ""
        args_str = "without args"
    
    info(f"Submitting {script} {args_str} at {rundir}")
    
    subprocess.run(f"sbatch --parsable {script} {args}", cwd=rundir, 
            shell=True, text=True, stderr=subprocess.STDOUT)

