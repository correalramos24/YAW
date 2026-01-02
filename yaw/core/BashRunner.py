
from .AbstractFilesRunner import AbstractFilesRunner

from utils.bash_script import BashScript

from pathlib import Path


class BashRunner(AbstractFilesRunner):
    """Run scripts or commands in bash."""

    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "bash_cmd": (None, "Script to execute (./s.sh) or command (ls)", "R"),
            "args" : (None, "Script arguments", "O"),
            "wrapper" : (None, "execute your command with a wrapper", "O"),
            "script_name" : ("yaw_wrapper.sh", "Bash script name", "O"),
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()
        self.script_path = Path(self.rundir, self.script_name)
        self.bash_script = BashScript(self.script_path)

    def run(self):
        self.bash_script.with_cmds(
            [self._get_env_str(),
             self._get_env_trk_str(),
             self._get_cmd_str(),]
        )

        if self.check_dry(): 
            self.bash_script.dry()
        else:
            self.bash_script.with_args(self.args).with_log(self.log_path).run()
            if self.bash_script.ret_code(): 
                self.set_result(0, "OK")
            else: 
                self.set_result(-1, "Return code !=0")

    def _get_env_str(self) -> str:
        if self.env_file: 
            return f"source {self.env_file}"
        else:
            return ""

    def _get_env_trk_str(self) -> str:
        """Get track env string."""
        if self.track_env: 
            return f"printenv &> {self.track_env}"
        else:
            return ""

    def _get_cmd_str(self) -> str:
        """Get the command string to execute."""
        ret = ""
        if self.wrapper:
            ret += f"{self.wrapper} "
        ret += self.bash_cmd
        if self.args:
            ret += " " + "".join(self.args)
        return ret
