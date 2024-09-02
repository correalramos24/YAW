

from .BashRunner import BashRunner
from .AbstractRunner import AbstractRunner
from utils import *
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class SlurmRunner(AbstractRunner):
    type: str = "SlurmRunner"
    # REQUIRED:
    slurm_nodes: int = None
    slurm_mpi: int = None
    slurm_cpus: int = None
    
    # OPTIONAL PARAMETERS:
    args : str = None
    slurm_queue : str = None
    slurm_account : str = None
    slurm_wait : bool = None
    slurm_time_limit : str = None
    slurm_contiguous : bool = None
    slurm_other_cmds : str = None
    WRAPPER_NAME="slurm_wrapper.slurm"

    def __post_init__(self):
        self.req_param = deepcopy(self.req_param)
        self.req_param.extend(["slurm_nodes", "slurm_mpi", "slurm_cpus"])
        super().__post_init__()
        self.slurm_workdir = Path(self.rundir)


    def manage_parameters(self):
        super().manage_parameters()
        #TODO: Check correctness of slurm parameters!

    def _inflate_runner(self):
        slurm_directives = {k : v for k, v in self.__dict__.items() 
                            if k.startswith("slurm_") and v }
        generate_slurm_script(Path(self.rundir, self.WRAPPER_NAME),
                              slurm_directives,
            [
                f"source {self.env_file}" if self.env_file else "",
                "printenv &> env.log",
                f"{self.bash_cmd}"
            ], self.log_name
        )

    def run(self):
        self._inflate_runner()
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_slurm_script(self.WRAPPER_NAME, self.args,
                                 self.rundir)

    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "SLURM PARAMETERS"),
            ("slurm_nodes", "Nodes"),
            ("slurm_mpi", "Tasks per node"),
            ("slurm_cpus", "Cpus per task"),
            ("slurm_queue", "queue for the submission"),
            ("slurm_account", "slurm account"),
            ("slurm_wait", "block the execution of sbatch until job end?"),
            ("slurm_time_limit", "time_limit in SLURM format (DD:HH:MM:SS)"),
            ("slurm_contiguous", "place contiguous nodes?"),
            ("slurm_other_cmds", "other slurm commands"),
        ])
        return parameters_info
