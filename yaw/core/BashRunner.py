
from .AbstractRunner import AbstractRunner
from dataclasses import dataclass
from pathlib import Path
from utils import *

@dataclass
class BashRunner(AbstractRunner):
    type: str = "BashRunner"
    bash_cmd: str = None
    args: str = None
    WRAPPER_NAME = "bash_wrapper.sh"

    def __post_init__(self):
        super().__post_init__()

    def manage_parameters(self):
        super().manage_parameters()

    def run(self):
        self.inflate_runner()
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_script(self.WRAPPER_NAME, self.args,
                           self.rundir, self.log_path)
    
    def inflate_runner(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        generate_bash_script(Path(self.rundir, self.WRAPPER_NAME),
            [
            load_env_cmd,
            "printenv &> env.log",
            f"{self.bash_cmd} $@"
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
            ("bash_cmd", "Script to be executed (./s.sh) or bash command (ls)"),
            ("args", "Script arguments")
        ])
        return parameters_info