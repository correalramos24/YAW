from .BashRunner import BashRunner
from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *
from pathlib import Path


class BashSlurmRunner(BashRunner, AbstractSlurmRunner):
    
    inv_BorS_msg = "bash_or_slurm must be slurm or bash, got: "
    
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
        
    def check_parameters(self):
        super().check_parameters()
        if self.__is_slurm():
            if not self.slurm_nodes or not self.slurm_queue or not self.slurm_account:
                raise Exception("If using SLURM, you must specify slurm_nodes, queue and account!")
            self._log("Using SLURM to execute the script")
        elif self.__is_bash():
            self._log("Using bash to execute the script")
        else:
            raise Exception(BashSlurmRunner.inv_BorS_msg + self.bash_or_slurm)
        
    def manage_parameters(self):
        if self.__is_slurm(): AbstractSlurmRunner.manage_parameters(self)
        elif self.__is_bash(): BashRunner.manage_parameters(self)
        self.wrapper_script = Path(self.rundir, self.script_name)
    
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
        if self.check_dry(): return
        elif self.__is_slurm():
            execute_slurm_script(self.wrapper_script, None, self.rundir)
            self.set_result(0, "SUBMITTED")
        elif self.__is_bash():
            r = execute_script( 
                script = self.wrapper_script, 
                args = self.args,
                rundir = self.rundir,
                log_file = self.log_path
            )
            if not r: self.set_result(0, "OK")
            else: self.set_result(-1, "Return code !=0")
        else:
            raise Exception(BashSlurmRunner.inv_BorS_msg + self.bash_or_slurm)

    def __is_slurm(self) -> bool: return self.bash_or_slurm.lower() == "slurm"
    def __is_bash(self) -> bool: return self.bash_or_slurm.lower() == "bash"