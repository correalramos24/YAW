

from .BashRunnerRundir import BashRunnerRundir
from .AbstractRunner import AbstractRunner
from utils import *
from dataclasses import dataclass

@dataclass
class SlurmRunner(BashRunnerRundir):
    type: str = "SlurmRunner"
    # REQUIRED:
    slurm_nodes: int = None
    slurm_mpi: int = None
    slurm_cpus: int = None
    
    # OPTIONAL PARAMETERS:
    slurm_queue : str = None
    slurm_account : str = None
    slurm_wait : bool = None
    slurm_time_limit : str = None
    slurm_contiguous : bool = None
    slurm_other_cmds : str = None
    WRAPPER_NAME="slurm_wrapper.slurm"

    def __post_init__(self):
        super().__post_init__()
        self.slurm_workdir = Path(self.rundir) # Pass rundir to SLURM script

    def manage_parameters(self):
        super().manage_parameters()

    def run(self):
        self.inflate_wrapper()
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_slurm_script(self.WRAPPER_NAME, self.args, self.rundir)

    def inflate_wrapper(self):
        generate_slurm_script(Path(self.rundir, self.WRAPPER_NAME),
            self.log_name, self._get_slurm_directives(),
            [
                f"source {self.env_file}" if self.env_file else "",
                "printenv &> env.log",
                f"{self.bash_cmd}"
            ]
        )

    # PARAMETER METHODS:
    @classmethod
    def get_required_params(self) -> list[str]:
        return super().get_required_params() + ["slurm_nodes", "slurm_mpi", "slurm_cpus"]

    # YAML GENERATION METHODS:
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

    def _get_slurm_directives(self) -> dict:
        return {k : v for k, v in self.__dict__.items() 
                    if k.startswith("slurm_") and v }