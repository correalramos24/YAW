
from .AbstractRunner import AbstractRunner
from utils import *


class AbstractSlurmRunner(AbstractRunner):
    """
    Basic runner to handle (the submission of) slurm jobs.
    """
    
    @classmethod
    def get_runner_type(cls) -> str:
        return "SlurmRunner"

    @classmethod
    def get_params_dict(cls):
        aux =  super().get_params_dict()
        aux.update({
            "slurm_nodes": (None, "Number of nodes to use", "R"),
            "slurm_mpi": (None, "Number of MPI tasks per node", "R"),
            "slurm_cpus": (None, "Number of CPUs per task", "R"),
            "slurm_queue": (None, "Queue to use", "O"),
            "slurm_account": (None, "Slurm account to use", "O"),
            "slurm_wait": (None, "Wallclock", "O"),
            "slurm_time_limit": (None, "Time limit for the job (DD:HH:MM:SS)", "O"),
            "slurm_contiguous": (None, "place contiguous nodes?", "O"),
            "slr_other_cmds": (None, "Other slurm commands", "O"),
            "slr_wrapper_name": ("slurm_yaw.slurm", "slurm script wrapper name. slurm_yaw.slurm by def.", "O"),
        })
        return aux

    #===============================PRIVATE METHODS=============================
    
    def _get_slurm_directives(self):
        return {
            directive: value for directive, value 
            in self.slurm_directives.items()
            if directive.startswith("slurm_") and value
        }
    


