
from core import AbstractRunner
from utils import *

from dataclasses import dataclass
from pathlib import Path

@dataclass
class CompileIfsBundle(AbstractRunner):
    
    type: str = "CompileIfsBundle"
    dry: bool = False
    arch: Path = None
    build_dir   : str = "build"
    script_name : str = "yaw_compile"
    recompile   : bool = False
    bundle_env  : bool = None
    build_jobs  : int  = 80   

    def __post_init__(self):
        super().__post_init__()
        self.arch_path = Path(self.rundir, self.arch) if self.arch else None
        self.bundle_env = Path(self.bundle_env) if self.bundle_env else None
    
    # EXECUTION
    def manage_parameters(self):
        super().manage_parameters()
        if self.recompile:
            warning("Force recompile enabled!")
        check_path_exists_exception(self.arch_path)
        check_file_exists_exception(self.bundle_env)

    def run(self):
        self.inflate_runner()
        if self.dry:
            print("DRY MODE: Not executing anything")
            return True
        elif check_path_exists(Path(self.rundir, self.build_dir)) and not self.recompile:
            warning("Build directory already created!")
            print("recompile option not set, skipping")
        else:
            r = execute_script(Path(self.rundir, self.script_name), "", 
                               self.rundir, self.log_path)
            if not r:
                print("Executed sucesfully", r)
            else:
                print("Return code != 0", r)
        return r == 0

    def inflate_runner(self):
        bundle_env_str = f"source {self.bundle_env}" if self.bundle_env else ""
        generate_bash_script(Path(self.rundir, self.script_name),
            ["# AUTOMATED SCRIPT GENERATION",
            bundle_env_str,
            "./ifs-bundle create",
            f"./ifs-bundle build --arch {self.arch} --with-single-precision \
            --with-double-precision-nemo --nemo-version=V40 \
            --nemo-grid-config=eORCA1_GO8_Z75 --nemo-ice-config=SI3 \
            --with-multio-for-nemo-sglexe --dry-run --verbose \
            --nemovar-grid-config=ORCA1_Z42 --nemovar-ver=DEV --build-dir={self.build_dir}",
            f"cd {self.build_dir}",
            "./configure.sh",
            f"source env.sh && make -j {self.build_jobs}"
             ]
        )

    # PARAMETER METHODS:
    @classmethod
    def get_required_params(cls) -> list[str]:
        return super().get_required_params() + ["arch"]
    

    # YAML GENERATION METHODS:
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "IFS-Bundle parameters"),
            ("dry", "Dry mode: Only generate script"),
            ("arch", "IFS-Bundle arch (path format not starting with /)"),
            ("bundle_env", "Override bundle env with a script (absolute path)"),
            ("build_dir", "build directory name. Default: build"),
            ("script_name", "wrapper name"),
            ("recompile", "Force recompile (True/False). Default: False"),
            ("build_jobs", "Build jobs to be used")

        ])
        return parameters_info