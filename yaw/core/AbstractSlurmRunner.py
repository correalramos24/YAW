
from .AbstractRunner import AbstractRunner
from utils import *


class AbstractSlurmRunner(AbstractRunner):
    """
    Basic runner to handle (the submission of) slurm jobs.
    """
    
    def __init__(self, **parameters):
        super().__init__(**parameters)
        self.wrapper_name = self._get_parameter_value("wrapper_name", "slurm_yaw.slurm")
        self.slurm_directives = {k : v for k, v in self.parameters.items()
                                 if k.startswith("slurm_") and v}

    #===============================PARAMETER METHODS===========================

    @classmethod
    def get_runner_type(cls) -> str:
        return "SlurmRunner"

    @classmethod
    def get_parameters(cls) -> list[str]:
        return super().get_parameters() + \
            ["slurm_nodes", "slurm_mpi", "slurm_cpus", "slurm_queue", "slurm_account", 
            "slurm_wait", "slurm_time_limit", "slurm_contiguous", "slurm_other_cmds"]

    @classmethod
    def get_required_params(cls) -> list[str]:
        ret = super().get_required_params()
        return  ret + ["slurm_nodes", "slurm_mpi", "slurm_cpus"]

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "SLURM PARAMETERS"),
            ("wrapper_name", "slurm script wrapper name. slurm_yaw.slurm by def.")
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