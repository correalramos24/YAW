from .BashRunner import BashRunner
from .SlurmRunner import SlurmRunner
from utils import *
from pathlib import Path


class BashSlurmRunner(SlurmRunner, BashRunner):
    """
    Run scripts or commands in bash with slurm.
    """

    @classmethod
    def get_runner_type(cls) -> str:
        return "BashSlurmRunner"
    
    def run(self):
        info("Generatig SLURM script....")
        wrapper_cmd = f"{self._gp("wrapper")} " if self._gp("wrapper") else ""
        args_str = self._gp("args") if self._gp("args") else ""
        generate_slurm_script(
            f_path=Path(self._gp("rundir"), self._gp("slr_wrapper_name")), 
            log_file=self.get_log_path(),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
                f"source {self._gp("env_file")}" if self._gp("env_file") else "",
                f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
                f"{wrapper_cmd}{self._gp("bash_cmd")} {args_str}"
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
