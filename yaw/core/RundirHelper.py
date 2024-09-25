
from .AbstractRunner import AbstractRunner
from utils import *
from dataclasses import dataclass
from pathlib import Path
import tarfile

@dataclass
class RundirHelper(AbstractRunner):
    """Contain the minimum parameters to run something with
    a rundir.
    """
    type: str = "RundirHelper"
    rundir : Path = None
    force  : bool = False
    ref_rundir : Path = None
    rundir_files : list[Path] = None
    tar_gz_files : list[Path] = None

    def __post_init__(self):
        super().__post_init__()
        self.rundir = Path(self.rundir) if self.rundir else None
        self.ref_rundir = Path(self.ref_rundir) if self.ref_rundir else None
        self.rundir_files = [Path(f) for f in self.rundir_files] \
            if self.rundir_files else None
        self.tar_gz_files = [Path(f) for f in self.tar_gz_files] \
            if self.tar_gz_files else None
        if not self.ref_rundir and not self.rundir_files:
            warning("Not selected ref_rundir or rundir_files")
        if self.force:
            warning("FORCE MODE ENABLED!")

    def manage_parameters(self):
        super().manage_parameters()
        if self.rundir:
            info(f"Using {self.rundir} as rundir")
            if not check_path_exists(self.rundir):
                create_dir(self.rundir)
            elif check_path_exists(self.rundir) and not self.force:
                raise Exception(f"{self.rundir} already exists, ABORTING!")
        if self.ref_rundir:
            copy_folder(self.ref_rundir, self.rundir, True)
        if self.rundir_files:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))
        if self.tar_gz_files:
            for f in self.tar_gz_files:
                check_file_exists_exception(f)
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self.rundir)


    # PARAMETER METHODS:
    @classmethod
    def get_required_params(self):
        return super().get_required_params() + ["rundir"]
    
    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        ret = super().get_multi_value_params()
        ret.add("files_rundir")
        ret.add("tar_gz_files")
        return ret
    
    # YAML GENERATION METHODS:
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[str]:
        params_info = super()._inflate_yaml_template_info()
        params_info.extend([
            ("comment", "RUNDIR PARAMETERS"),
            ("rundir", "Rundir path to execute the runner."),
            ("force", "Overwrite previous content of rundir"),
            ("ref_rundir", "Reference rundir to use, (copy all to rundir)"),
            ("rundir_files", "List of files to copy to the rundir"),
            ("tar_gz_files", "List of tar.gz. files to uncompress into the rundir")
        ])
        return params_info
