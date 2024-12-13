
from .AbstractRunner import AbstractRunner
from pathlib import Path
from utils import *

class BashRunner(AbstractRunner):

    def __init__(self, **parameters):
        super().__init__(**parameters)
        self.wrapper = self._get_parameter_value("wrapper")
        self.track_env = self._get_parameter_value("track_env")
        self.script_name = self._get_parameter_value("script_name", "bash_wraper.sh")

    def manage_multi_recipie(self):
        super().manage_multi_recipie()
        if self.script_name and not "script_name" in self.multi_params:
            info(f"Adding {self.recipie_name} to script_name")
            self.script_name = f"{self.recipie_name}_{self.script_name}"

    def run(self):
        #1. Generate bash script:
        wrapper_cmd = f"{self.wrapper}" if self.wrapper else ""
        generate_bash_script(Path(self.rundir, self.script_name),[
            f"source {self.env_file}" if self.env_file else "",
            f"printenv &> {self.track_env}" if self.track_env else "",
            f"{wrapper_cmd} {self._get_parameter_value("bash_cmd")} $@"
            ]
        )
        #2. Execute:
        if self.dry: print("DRY MODE: Not executing anything!")
        else:
            r = execute_script( self.script_name, self._get_parameter_value("args"),
                                self.rundir, self.log_path)
            if not r: print("Executed sucesfully", r)
            else: print("Return code != 0", r)
            return r == 0

    #===============================PARAMETER METHODS===========================
    @classmethod
    def get_runner_type(cls) -> str:
        return "BashRunner"

    @classmethod
    def get_parameters(cls) -> list[str]:
        return super().get_parameters() + \
            ["wrapper", "bash_cmd", "args", "script_name", "track_env"]

    @classmethod
    def get_required_params(cls) -> list[str]:
        return super().get_required_params() + ["bash_cmd"]

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "BASH PARAMETERS"),
            ("wrapper", "execute your command with a wrapper"),
            ("bash_cmd", "Script to be executed (./s.sh) or bash command (ls)"),
            ("args", "Script arguments"),
            ("script_name", "wrapper name"),
            ('track_env', "File name to store the env of a run")
        ])
        return parameters_info