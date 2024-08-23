
from abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from utils import *
from pathlib import Path

@dataclass
class bashRunner(AbstractRunner):
    type : str = "bashRunner"
    script: Path = None
    args : str = field(default=None)
    ref_rundir : Path = field(default=None)
    rundir_files : list[Path] = field(default=None)
    WRAPPER_NAME="bash_wrapper.sh"
    
    def __post_init__(self):
        super().__post_init__()
        self.script = Path(self.script) if self.script else None
        
        self.ref_rundir = Path(self.ref_rundir) if self.ref_rundir else None
        
        if isinstance(self.args, list) :
            self.args = ' '.join(self.args)

        if not self.rundir and not self.script :
            raise Exception("rundir and script are required arguments!")
        if not self.ref_rundir and not self.rundir_files:
            raise Exception("Either ref_rundir or rundir_files are required")
        
        self.rundir_files = [Path(f) for f in self.rundir_files] \
                            if self.rundir_files else None

    def manage_parameters(self):
        super().manage_parameters()
        
        # Manage reference_rundir:
        if self.ref_rundir is not None:
            copy_folder(self.ref_rundir, self.rundir, True)
        elif self.rundir_files is not None:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))
        else:
            raise Exception("Logic exception, you must see this msg!")
            

    def run(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        super().generate_bash_wrapper(Path(self.rundir, self.WRAPPER_NAME),
            [
                load_env_cmd,
                f"./{self.script} $@"
            ]
        )
        
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_script(self.WRAPPER_NAME, self.args, 
                           self.rundir, self.log_name)