

from bash_runner import bashRunner
from dataclasses import dataclass, field
from utils import *

@dataclass
class slurmRunner(bashRunner):

    nodes: list[int] = None
    mpi_per_node: list[int] = None
    cpu_per_node: list[int] = None

    def __post_init__(self):
        super().__post_init__()
    
        # Manage input as strings!
    
        self.nodes = [self.nodes] if isinstance(self.nodes, int) else self.nodes
        self.mpi_per_node = [self.mpi_per_node] \
                                if isinstance(self.mpi_per_node, int) \
                                else self.mpi_per_node
        self.cpu_per_node = [self.cpu_per_node] \
                                if isinstance(self.cpu_per_node, int) \
                                else self.cpu_per_node


    def manage_parameters(self):
        super().manage_parameters()
        # Check if we only have 1 run or more...

    def run(self):
        
        #TODO: Non-defined parameters must pick the default values form script!

        for node in self.nodes:
            for mpi in self.mpi_per_node:
                for omp in self.cpu_per_node:
                    print(f"Running {self.script} with "
                          f"{node} nodes, {mpi} tasks per node "
                          f"and {omp} cpus per task "
                          f"at {self.rundir}")
