from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *

class SlurmRunner(AbstractSlurmRunner):

    def manage_multi_recipie(self):
        #TODO: Add logic to add Nodes x MPI per node x cpu per node.
        super().manage_multi_recipie()
        
        if self.all_same_rundir:
            self.runner_print("Need to tune parameters for multirecipie!")
            self._sp("slr_wrapper_name", f"{self.recipie_name()}_{self._gp('slr_wrapper_name')}")

    def run(self):
        info("Generatig SLURM script....")
        generate_slurm_script(
            f_path=Path(self._gp("rundir"), self._gp("slr_wrapper_name")), 
            log_file=self.get_log_path(),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
                f"source {self._gp("env_file")}" if self._gp("env_file") else "",
                f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
                "echo \"Holi\"",
                "pwd"
            ]
        )
        if self._gp("dry"):
            print("DRY MODE: Not executing anything!")
            self.runner_result = "DRY MODE TRUE"
            self.runner_status = "DRY"
        else:
            execute_slurm_script(self._gp("slr_wrapper_name"), None, self._gp("rundir"))
            self.runner_result = "0"
            self.runner_status = "SUBMITTED"

