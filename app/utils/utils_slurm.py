
from pathlib import Path
from .utils_print import *
from pathlib import Path
import subprocess
from .utils_print import *

slurm_syntax = {
    "nodes" : "-N", "mpi" : "--ntasks-per-node", "cpus" : "-c",
    "account": "-A", "queue" : "--qos", "time_limit" : "--time",
    "wait" : "-W","contiguous" : "--contiguous",
}

def generate_slurm_script(f_path: Path,
                          slurm_directives : dict[str, any],
                          cmds : list[str]):
    formatted_directives = ""
    for directive, val in slurm_directives.items():
        aux = directive.replace("slurm_","")
        formatted_directives += f"#SBATCH {slurm_syntax[aux]} {val}\n"
    
    cmds_with_end_line = '\n'.join(cmds)
    with open(f_path, mode="w") as bash_file:
        bash_file.write(f"""#!/bin/bash
{formatted_directives}                        
{"="*80}
# AUTOMATED SLURM SCRIPT WRAPPER GENERATION:\n
{cmds_with_end_line}
{"="*80}
""")
        log(f"Created", f_path)

def execute_slurm_script(script, args, rundir, log_file=None):
    if args:
        args_str = "with " + args
    else: 
        args = ""
        args_str = "without args"
    if log_file:
        info(f"Submitting {script} {args_str} at {rundir}, writting STDOUT to {log_file}")
        file_desc = open(log_file, mode="w")
    else:
        info(f"Submitting {script} {args_str} at {rundir}")
        file_desc = None

    r = subprocess.run(f"sbatch --parsable {script} {args}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT, stdout=file_desc)

    if log_file is not None:
        file_desc.close()
