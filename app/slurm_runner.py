

from abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from utils import *

@dataclass
class slurmRunner(AbstractRunner):

    nodes: list[int] = field(default_factory=list)
    mpi_per_node: list[int] = field(default_factory=list)
    cpu_per_node: list[int] = field(default_factory=list)
    ref_rundir: Path = None
    script: Path = None
    script_in_rundir: bool = True
    dry_mode :bool = False

    def check_parameters(self):
        print("Checking parameters...")

    def run(self):
        for nodes in self.nodes:
            print(f"Running {self.script} with {nodes}")
