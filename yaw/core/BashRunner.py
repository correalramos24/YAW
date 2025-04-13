
from .AbstractRunner import AbstractRunner
from pathlib import Path
from utils import *

class BashRunner(AbstractRunner):
    """
    Run scripts or commands in bash.
    """
    @classmethod
    def get_runner_type(cls) -> str:
        return "BashRunner"

    @classmethod
    def get_params_dict(cls):
        aux = super().get_params_dict()
        aux.update({
            "wrapper" : (None, "execute your command with a wrapper", "O"),
            "bash_cmd": (None, "Script to execute (./s.sh) or command (ls)", "R"),
            "args" : (None, "Script arguments", "O"),
            "script_name" : ("yaw_wrapper.sh", "Bash script name", "O"),
            "track_env" : ("env.log", "File name to store the env of a run", "O")
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()
        
        
    def manage_multi_recipie(self):
        if not self.all_same_rundir:
            self.runner_print("No need to tune parameters for multirecipie!")
        else:
            self.runner_print("Tunning parameters for multirecipie!")
            self._sp("rundir", Path(self._gp("rundir"), self.recipie_name()))
            self.runner_info("Update rundir with recipie name", self._gp("rundir"))


    def run(self):
        #1. Generate bash script:
        wrapper_cmd = f"{self._gp("wrapper")} " if self._gp("wrapper") else ""
        args_str = self._gp("args") if self._gp("args") else ""
        generate_bash_script(Path(self._gp("rundir"), self._gp("script_name")),[
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            f"{wrapper_cmd}{self._gp("bash_cmd")} {args_str}"
            ]
        )
        #2. Execute:
        if self._gp("dry"): 
            print("DRY MODE: Not executing anything!")
            ret = "DRY EXECUTION!"
            self.runner_result = "DRY"
        else:
            r = self.runner_result = execute_script( 
                script = self._gp("script_name"), 
                args = self._gp("args"),
                rundir = self._gp("rundir"),
                log_file = self.get_log_path()
            )
            if not r: self.runner_result_str = "OK"
            else: self.runner_result_str = "Return code !=0"
         

