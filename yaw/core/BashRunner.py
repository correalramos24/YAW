
from .AbstractRunner import AbstractRunner
from dataclasses import dataclass
from pathlib import Path
from utils import *

@dataclass
class BashRunner(AbstractRunner):
    type: str = "BashRunner"
    wrapper: str = None
    bash_cmd: str = None
    args: str = None
    script_name : str = None
    dry: bool = False
    track_env : str = None

    def __post_init__(self):
        super().__post_init__()
        if not self.script_name:
            self.script_name = "bash_wrapper.sh"

    def run(self) -> bool:
        self.inflate_runner()
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            r = execute_script(self.script_name, self.args, 
                               self.rundir, self.log_path)
            if not r:
                print("Executed sucesfully", r)
            else:
                print("Return code != 0", r)
        return r == 0
    
    def inflate_runner(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        trck_env_cmd = f"printenv &> {self.track_env}" if self.track_env else ""
        wrapper_cmd = f"{self.wrapper}" if self.wrapper else ""
        generate_bash_script(Path(self.rundir, self.script_name),
            [
            load_env_cmd,
            trck_env_cmd,
            f"{wrapper_cmd} {self.bash_cmd} $@"
            ]
        )
        
    # PARAMETER METHODS:
    @classmethod
    def get_required_params(self) -> list[str]:
        return super().get_required_params() + ["bash_cmd"]

    # YAML GENERATION METHODS:
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