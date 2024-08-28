from .AbstractRunner import AbstractRunner
from dataclasses import dataclass, field
from pathlib import Path
from app.utils import *


@dataclass
class BashRunner(AbstractRunner):
    type: str = "bash_runner"
    bash_cmd: Path = None
    args: str = None
    ref_rundir: Path = None
    rundir_files: list[Path] = None
    WRAPPER_NAME = "bash_wrapper.sh"

    def __post_init__(self):
        # ADD REQ_PARAMS FOR THIS RUNNER:
        self.req_param.extend(["bash_cmd"])

        # MANAGE PARAMETER TYPES:
        self.bash_cmd = Path(self.bash_cmd) if self.bash_cmd else None
        self.ref_rundir = Path(self.ref_rundir) if self.ref_rundir else None
        self.rundir_files = [Path(f) for f in self.rundir_files] \
            if self.rundir_files else None

        if not self.ref_rundir and not self.rundir_files:
            warning("Not selected ref_rundir or rundir_files")

        # INIT SUPER CLASS:
        super().__post_init__()

    def manage_parameters(self):
        super().manage_parameters()

        # MANAGE RUNDIR FILES:
        if self.ref_rundir is not None:
            copy_folder(self.ref_rundir, self.rundir, True)
        if self.rundir_files is not None:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))

    def inflate_runner(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        print(self.rundir)
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

    @staticmethod
    def _inflate_yaml_template_info() -> list[(str, str)]:
        parameters_info = AbstractRunner._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "BASH PARAMETERS"),
            ("bash_cmd", "Script to be executed (./your_script.sh) or bash command (ls)"),
            ("args", "Script arguments"),
            ("ref_rundir", "Reference rundir to use, (copy all to rundir)"),
            ("rundir_files", "List of files to copy to the rundir")
        ])
        return parameters_info