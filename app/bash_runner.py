
from abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from utils import *
from pathlib import Path
from typing import Optional
import os

@dataclass
class bashRunner(AbstractRunner):
    script: Path
    rundir: Path
    env_file: Optional[Path] = field(default=None)
    args : Optional[str] = field(default=None)
    log_name : Optional[str] = field(default=None)
    ref_rundir : Optional[Path] = field(default=None)
    rundir_files : Optional[list[Path]] = field(default=None)

    def __post_init__(self):
        super().__post_init__()
        self.script = Path(self.script) if self.script is not None else None
        self.rundir = Path(self.rundir) if self.rundir is not None else None
        self.env_file = Path(self.env_file) if self.env_file is not None else None
        self.ref_rundir = Path(self.ref_rundir) if self.ref_rundir is not None else None
        
        if self.args is list:
            self.args = ' '.join(self.args)

        if self.rundir is None and self.script is None:
            raise Exception("rundir and script are required arguments!")
        if self.ref_rundir is None and self.rundir_files is None:
            raise Exception("Either ref_rundir or rundir_files is required")
        
        self.rundir_files = [Path(f) for f in self.rundir_files] if self.rundir_files is not None else None

    def manage_parameters(self):
        # Manage rundir:
        if not check_path_exists(self.rundir):
            create_dir(self.rundir)
            print(f"Using {self.rundir} as rundir")
        else:
            print(f"WARNING, rundir {self.rundir} already exists!")
        
        # Manage reference_rundir:
        if self.ref_rundir is not None:
            copy_folder(self.ref_rundir, self.rundir, True)
        elif self.rundir_files is not None:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))

        else:
            raise Exception("Logic exceptio, you must see this msg!")
        # Manage log file
        if self.log_name is None:
            print("Not using a log to store the results, appending to STDOUT")
            

    def run(self):
        with open(Path(self.rundir, "run_wrapper.sh"), mode="w") as bash_file:
            bash_file.write(f"""
#!/bin/bash
source {self.env_file}
./{self.script} $@
                            """)
        print("Created run script!")
        execute_script("./run_wrapper.sh", self.args, self.rundir, self.log_name)          