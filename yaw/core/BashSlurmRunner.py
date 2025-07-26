from .BashRunner import BashRunner
from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *
from pathlib import Path


class BashSlurmRunner(AbstractSlurmRunner, BashRunner):
    
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
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
        self.wrapper_script = Path(self._gp("rundir"), self._gp("slr_wrapper_name"))
    
    def run(self):
        info("Generatig SLURM script....")
        generate_slurm_script(f_path=self.wrapper_script, log_file=self.get_log_path(),
            slurm_directives=self._get_slurm_directives(), cmds=
            [
                self._get_env_str(),
                self._get_env_trk_str(),
                self._get_cmd_str(),
            ]
        )
        if self._gp("dry"):
            print("DRY MODE: Not executing anything!")
            self.set_runnner_result(0, "DRY RUN")
        elif self._gp("bash_or_slurm").lower() == "slurm":
            execute_slurm_script(self._gp("slr_wrapper_name"), None, self._gp("rundir"))
            self.set_runner_result(0, "SUBMITTED")
        elif self._gp("bash_or_slurm").lower() == "bash":
            r = self.runner_result = execute_script( 
                script = self._gp("slr_wrapper_name"), 
                args = self._gp("args"),
                rundir = self._gp("rundir"),
                log_file = self.get_log_path()
            )
            if not r: self.set_runner_result(0, "OK")
            else: self.set_runner_result(-1, "Return code !=0")
