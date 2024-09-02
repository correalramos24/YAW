from _ast import List

from .AbstractRunner import AbstractRunner
from dataclasses import dataclass, field
from pathlib import Path
from utils import *
from copy import deepcopy

@dataclass
class BashRunner(AbstractRunner):
    type: str = "bash_runner"
    bash_cmd: Path = None
    args: str = None
    WRAPPER_NAME = "bash_wrapper.sh"

    def __post_init__(self):
        # ADD REQ_PARAMS FOR THIS RUNNER:
        self.req_param = deepcopy(self.req_param)
        self.req_param.extend(["bash_cmd"])
        # INIT SUPER CLASS:
        super().__post_init__()
        # MANAGE PARAMETER TYPES:
        self.bash_cmd = Path(self.bash_cmd) if self.bash_cmd else None


    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        params = super().get_multi_value_params()
        params.add("rundir_files")
        return params

    def manage_parameters(self):
        super().manage_parameters()

    def inflate_runner(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        if not self.rundir:
            self.rundir = os.getcwd()
            info("Not found rundir, running at", self.rundir)
        generate_bash_script(Path(self.rundir, self.WRAPPER_NAME),
            [
            load_env_cmd,
            "printenv &> env.log",
            f"{self.bash_cmd} $@"
            ]
        )

    def run(self):
        self.inflate_runner()
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_script(self.WRAPPER_NAME, self.args,
                           self.rundir, self.log_name)

    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "BASH PARAMETERS"),
            ("bash_cmd", "Script to be executed (./your_script.sh) or bash command (ls)"),
            ("args", "Script arguments")
        ])
        return parameters_info