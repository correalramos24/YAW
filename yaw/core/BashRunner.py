
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

    def manage_multi_recipie(self):
        super().manage_multi_recipie()
        if self._gp("script_name") and not "script_name" in self.multi_params:
            info(f"Adding {self.recipie_name} to script_name")
            self.parameters["script_name"] =  f"{self.recipie_name}_{self.parameters["script_name"]}"

    def run(self):
        #1. Generate bash script:
        wrapper_cmd = f"{self._gp("wrapper")} " if self._gp("wrapper") else ""
        generate_bash_script(Path(self._gp("rundir"), self._gp("script_name")),[
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            f"{wrapper_cmd}{self._gp("bash_cmd")} $@"
            ]
        )
        #2. Execute:
        if self._gp("dry"): 
            print("DRY MODE: Not executing anything!")
            ret = "DRY EXECUTION!"
            r = 0
        else:
            r = execute_script( self._gp("script_name"), self._gp("args"),
                                self._gp("rundir"), self._gp("log_path"))
            if not r: ret = "Return code 0"
            else: ret = "Return code !=0"
        print(f"{ret} ({r})")
        return ret

