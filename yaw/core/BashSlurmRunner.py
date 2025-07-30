from .BashRunner import BashRunner
from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *
from pathlib import Path


class BashSlurmRunner(BashRunner, AbstractSlurmRunner):
    
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "bash_or_slurm" : ("slurm", "Select bash or slurm to execute the script", "R"),
            "slurm_nodes": (None, "Number of nodes to use", "O"),
            "slurm_queue": (None, "Queue to use", "O"),
            "slurm_account": (None, "Slurm account to use", "O"),
        })
        return aux
    
    def manage_parameters(self):
        if self._gp("bash_or_slurm") == "slurm":
            if not self._gp("slurm_nodes") or not self._gp("slurm_queue") or not self._gp("slurm_account"):
                raise Exception("If using SLURM, you must specify slurm_nodes, queue and account!")
            self.runner_info("Using SLURM to execute the script")
            AbstractSlurmRunner.manage_parameters(self)
        elif self._gp("bash_or_slurm") == "bash":
            self.runner_info("Using bash to execute the script")
            BashRunner.manage_parameters(self)
            
        else:
            raise Exception("bash_or_slurm must be slurm or bash; not |" + self._gp("bash_or_slurm"))
        self.wrapper_script = Path(self._gp("rundir"), self._gp("script_name"))
    
    def run(self):
        info("Generatig SLURM script....")
        generate_slurm_script(f_path=self.wrapper_script, log_file=self.log_path,
            slurm_directives=self._get_slurm_directives(), cmds=
            [
                self._get_env_str(),
                self._get_env_trk_str(),
                self._get_cmd_str(),
            ]
        )
        if self._gp("dry"):
            print("DRY MODE: Not executing anything!")
            self.set_result(0, "DRY RUN")
        elif self._gp("bash_or_slurm").lower() == "slurm":
            execute_slurm_script(self.wrapper_script, None, self._gp("rundir"))
            self.set_result(0, "SUBMITTED")
        elif self._gp("bash_or_slurm").lower() == "bash":
            r = execute_script( 
                script = self.wrapper_script, 
                args = self._gp("args"),
                rundir = self._gp("rundir"),
                log_file = self.log_path
            )
            if not r: self.set_result(0, "OK")
            else: self.set_result(-1, "Return code !=0")
