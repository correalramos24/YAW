
from .AbstractRunner import AbstractRunner
from utils import *
from abc import ABC, abstractmethod


class AbstractSlurmRunner(AbstractRunner, ABC):
    """
    Basic runner to handle (the submission of) slurm jobs.
    """
    
    @classmethod
    def get_params_dict(cls):
        aux =  super().get_params_dict()
        aux.update({
            "slurm_nodes": (None, "Number of nodes to use", "R"),
            "slurm_mpi": (None, "Number of MPI tasks per node", "O"),
            "slurm_cpus": (None, "Number of CPUs per task", "O"),
            "slurm_queue": (None, "Queue to use", "R"),
            "slurm_account": (None, "Slurm account to use", "R"),
            "slurm_wait": (False, "Wait sbatch until job finishes", "O"),
            "slurm_time_limit": (None, "Time limit for the job (DD:HH:MM:SS)", "O"),
            "slurm_contiguous": (None, "place contiguous nodes?", "O"),
            "slurm_job_name": ("yaw-job", "SLURM job name", "O"),
            "slr_other_cmds": (None, "Other slurm commands", "O"),
            "slr_wrapper_name": ("slurm_yaw.slurm", "slurm script wrapper name. slurm_yaw.slurm by def.", "O"),
        })
        return aux

    def manage_multi_recipie(self):
        #TODO: Add logic to add Nodes x MPI per node x cpu per node.
        super().manage_multi_recipie()
        if self._gp("same_rundir"):
            self.runner_print("Need to tune parameters for multirecipie!")
            self._sp("slr_wrapper_name", f"{self.recipie_name()}_{self._gp('slr_wrapper_name')}")
        elif self._gp("create_dir"):
            self._sp("rundir", Path(self._gp("rundir"), self.recipie_name()))
            self.runner_print("Updated rundir with recipie name", self._gp("rundir"))

    @abstractmethod
    def run(self):
        pass
    
    #===============================PRIVATE METHODS=============================
    
    def _get_slurm_directives(self):
        return {
            directive: value for directive, value 
            in self.parameters.items()
            if directive.startswith("slurm_") and value
        }
    


