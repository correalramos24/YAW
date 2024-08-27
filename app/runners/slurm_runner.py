

from .bash_runner import bashRunner
from dataclasses import dataclass
from utils import *

@dataclass
class slurmRunner(bashRunner):
    type: str = "slurm_runner"
    # Required:
    slurm_nodes: int = None
    slurm_mpi: int = None
    slurm_cpus: int = None
    
    # Optional arguments:
    slurm_queue : str = None
    slurm_account : str = None
    slurm_wait : bool = None
    slurm_time_limit : str = None
    slurm_contiguous : bool = None
    slurm_other_cmds : str = None
    WRAPPER_NAME="slurm_wrapper.slurm"

    def __post_init__(self):
        self.req_param.extend(["slurm_nodes", "slurm_mpi", "slurm_cpus"])
        super().__post_init__()


    def manage_parameters(self):
        super().manage_parameters()
        #TODO: Check correctness of slurm parameters!

    def run(self):
        slurm_directives = {k : v for k, v in self.__dict__.items() 
                            if k.startswith("slurm_") and v }
        generate_slurm_script(Path(self.rundir, self.WRAPPER_NAME),
            slurm_directives,
            [
                f"source {self.env_file}" if self.env_file else "",
                "printenv &> env.log",
                f"{self.script} $@"
            ]            
        )

        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_slurm_script(self.WRAPPER_NAME, self.args, 
                                 self.rundir, self.log_name)

       
    @classmethod
    def generate_yaml_template(cls):
        cls.req_param.extend(["nodes", "mpi_per_node", "cpu_per_node"])
        cls.help_dict.update({
            "slurm_nodes" : "Nodes to execute the script",
            "slurm_mpi" : "Tasks per node",
            "slurm_cpus" : "Cpus per task"
        })
        super().generate_yaml_template()