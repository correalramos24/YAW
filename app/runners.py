
from pathlib import Path
from dataclasses import dataclass, field



class AbstractRunner:
    
    def check_parameters(self):
        raise Exception("UNDEFINED RUN")

    def run(self):
        raise Exception("UNDEFINED RUN!")
    
@dataclass
class slurmRunner(AbstractRunner):

    nodes: list[int] = field(default_factory=list)
    mpi_per_node: list[int] = field(default_factory=list)
    cpu_per_node: list[int] = field(default_factory=list)
    ref_rundir: Path = None
    script: Path = None
    script_in_rundir: bool = True
    dry_mode :bool = False

    @staticmethod
    def empty_recipe():
        pass

    def run(self):
        for nodes in self.nodes:
            print(f"Running {self.script} with {nodes}")


