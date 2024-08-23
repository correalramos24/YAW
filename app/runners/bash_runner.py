
from .abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from pathlib import Path
from utils import *

@dataclass
class bashRunner(AbstractRunner):
    type : str = "bash_runner"
    script: Path = None
    args : str = field(default=None)
    ref_rundir : Path = field(default=None)
    rundir_files : list[Path] = field(default=None)
    WRAPPER_NAME="bash_wrapper.sh"
    

    def __post_init__(self):
        super().__post_init__()
        
        self.script = Path(self.script) if self.script else None
        self.ref_rundir = Path(self.ref_rundir) if self.ref_rundir else None
        self.rundir_files = [Path(f) for f in self.rundir_files] \
                            if self.rundir_files else None
        if isinstance(self.args, list) :
            self.args = ' '.join(self.args)

        if not self.rundir and not self.script :
            raise Exception("rundir and script are required arguments!")
        if not self.ref_rundir and not self.rundir_files:
            warning("Not selected ref_rundir or rundir_files")
        


    def manage_parameters(self):
        super().manage_parameters()
        
        # Manage reference_rundir:
        if self.ref_rundir is not None:
                copy_folder(self.ref_rundir, self.rundir, True)
        elif self.rundir_files is not None:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))
            

    def run(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        super().generate_bash_wrapper(Path(self.rundir, self.WRAPPER_NAME),
            [
                load_env_cmd,
                f"{self.script} $@"
            ]
        )
        
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_script(self.WRAPPER_NAME, self.args, 
                           self.rundir, self.log_name)
    
    @classmethod
    def generate_yaml_template(cls):
        cls.help_dict.update({
            "script" : "Script to be executed (can be a bash command)",
            "args" : "Script arguments",
            "ref_rundir" : "Reference rundir to use, (copy all to rundir)",
            "rundir_files" : "List of files to copy to the rundir"
        })
        super().generate_yaml_template()
