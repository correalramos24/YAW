
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

def generate_slurm_script(fPath: Path, 
                          slurm_directives : dict[str, any],
                          cmds : list[str]):
    foramtted_directives = ""
    for directive, val in slurm_directives.items():
        aux = directive.replace("slurm_","")
        foramtted_directives += f"#SBATCH {slurm_syntax[aux]} {val}\n" 
    
    cmds_with_endline = '\n'.join(cmds)
    with open(fPath, mode="w") as bash_file:
        bash_file.write(f"""#!/bin/bash
{foramtted_directives}                        
# AUTOMATED SLURM SCRIPT WRAPPER GENERATION:
{cmds_with_endline}
""")
        log(f"Created", fPath)

def execute_slurm_script(script, args, rundir, log_file=None):
    if not args: 
        args = ""
        args_str = "without args"
    else: 
        args_str = "with " + args
    if log_file is not None:
        info(f"Submitting {script} {args_str} at {rundir}, writting STDOUT to {log_file}")
        fdesc_stdout = open(log_file, mode="w") 
    else:
        info(f"Submitting {script} {args_str} at {rundir}")
        fdesc_stdout = None
    
    r = subprocess.run(f"sbatch {script} {args}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT, stdout=fdesc_stdout)

    if log_file is not None:
        fdesc_stdout.close()
