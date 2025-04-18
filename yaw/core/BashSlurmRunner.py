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
    
    @classmethod
    def get_params_dict(cls):
        aux = super().get_params_dict()
        aux.update({
            "bash_or_slurm" : ("slurm", "Select bash or slurm to execute the script", "R")
        })
        return aux
    
    def manage_parameters(self):
        if self._gp("bash_or_slurm") == "slurm":
            self.runner_info("Using SLURM to execute the script")
        elif self._gp("bash_or_slurm") == "bash":
            self.runner_info("Using bash to execute the script")
        else:
            raise Exception("bash_or_slurm must be slurm or bash; not |" + self._gp("bash_or_slurm"))
        super().manage_parameters()
        
    
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
        elif self._gp("bash_or_slurm").lower() == "slurm":
            execute_slurm_script(self._gp("slr_wrapper_name"), None, self._gp("rundir"))
            self.runner_result = "0"
            self.runner_status = "SUBMITTED"
        elif self._gp("bash_or_slurm").lower() == "bash":
            r = self.runner_result = execute_script( 
                script = self._gp("slr_wrapper_name"), 
                args = self._gp("args"),
                rundir = self._gp("rundir"),
                log_file = self.get_log_path()
            )
            if not r: self.runner_status = "OK"
            else: self.runner_status = "Return code !=0"
