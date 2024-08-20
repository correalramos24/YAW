
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class slurm_runner:

    nodes: list[int] = field(default_factory=list)
    mpi_per_node: list[int] = field(default_factory=list)
    cpu_per_node: list[int] = field(default_factory=list)
    ref_rundir: Path = None
    script: Path = None
    script_in_rundir: bool = True

    
    def run(self):
        print("Running the recipe!")

