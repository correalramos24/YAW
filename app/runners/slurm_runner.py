

from .bash_runner import bashRunner
from dataclasses import dataclass
from utils import *

@dataclass
class slurmRunner(bashRunner):
    type: str = "slurm_runner"
    nodes: list[int] = None
    mpi_per_node: list[int] = None
    cpu_per_node: list[int] = None

    def __post_init__(self):
        super().__post_init__()


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
    @classmethod
    def generate_yaml_template(cls):
        cls.help_dict.update({
            "nodes" : "Nodes to be used",
            "mpi_per_node" : "Tasks per node to be used",
            "cpu_per_node" : "CPU(s) per task to be used",
            "cartesian" : "Run all the parameter combinations."
        })
        super().generate_yaml_template()