
from .AbstractFilesRunner import AbstractFilesRunner
from pathlib import Path
from utils import *

class BashRunner(AbstractFilesRunner):
    """Run scripts or commands in bash."""

    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "bash_cmd": (None, "Script to execute (./s.sh) or command (ls)", "R"),
            "args" : (None, "Script arguments", "O"),
            "wrapper" : (None, "execute your command with a wrapper", "O"),
            "script_name" : ("yaw_wrapper.sh", "Bash script name", "O")
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()
        self.wrapper_script = Path(self.rundir, self.script_name)

    def run(self):
        generate_bash_script(self.wrapper_script,[
            self._get_env_str(),
            self._get_env_trk_str(),
            self._get_cmd_str(),
        ])
        self._info("Generated bash script:", self.script_name)

        if not self.check_dry():
            r = execute_script(
                script = self.script_name, args = self.args,
                rundir = self.rundir, log_file = self.log_path
            )
            if not r: self.set_result(0, "OK")
            else: self.set_result(-1, "Return code !=0")

    def _get_env_str(self) -> str:
        if self.env_file: return f"source {self.env_file}"
        else: return ""

    def _get_env_trk_str(self) -> str:
        """Get track env string."""
        if self.track_env: return f"printenv &> {self.track_env}"
        else: return ""

    def _get_cmd_str(self) -> str:
        """Get the command string to execute."""
        ret = ""
        if self.wrapper:
            ret += f"{self.wrapper} "
        ret += self.bash_cmd
        if self.args:
            ret += " " + "".join(self.args)
        return ret
