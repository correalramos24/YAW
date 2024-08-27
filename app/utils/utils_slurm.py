
from pathlib import Path
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
