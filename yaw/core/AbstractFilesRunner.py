
from .AbstractRunner import AbstractRunner

import utils.utils_files as ufiles
from utils.bash_cmd import BashCmd

import tarfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

REF_RD = {"desc": "Reference rundir to be used", 'kind': "O", "multi": True}
RD_FLS = {"desc": "List of files to copy to the rundir", "kind": "O", "multi": True} 
TRGZ_F = {"desc": "List of tar.gz. files to uncomp.", "kind": "O", "multi": True} 
GIT_RP = {"desc": "Git repository to clone and add to the rundir", "kind": "O"} 
GIT_BR = {"desc": "Git branch for git_repo", "kind": "O"} 
BIGLNK = {"desc": "Symlink big files from instead of copying them", "kind": "O"}


@dataclass(kw_only=True)
class AbstractFilesRunner(AbstractRunner):
    """
    Abstract class for runners that manage files.
    It provides methods to manage input files, output files and other use cases.
    """
    ref_rundir: Optional[set[str]] = field(default=None, metadata=REF_RD)
    rundir_files: Optional[set[str]] = field(default=None, metadata=RD_FLS)
    tar_gz_files: Optional[set[str]] = field(default=None, metadata=TRGZ_F)
    git_repo: Optional[str] = field(default=None, metadata=GIT_RP)
    git_branch: Optional[str] = field(default=None, metadata=GIT_BR)
    sym_link_big: bool = field(default=True, metadata=BIGLNK)

    def check_parameters(self):
        super().check_parameters()
        if self.git_branch and not self.git_repo:
            raise Exception("Git branch selected but repo not selected!")

        if self.git_repo:
            if self.git_branch:
                br_str = "Using branch: " + self.git_branch
            else:
                br_str = "Using default branch"
            self._log("Cloning repo", self.git_repo, br_str)

        if self.ref_rundir:
            for fldr in self.ref_rundir: 
                ufiles.check_path_exists_exception(fldr)

        if self.tar_gz_files:
            for f in [Path(f) for f in self.tar_gz_files]:
                ufiles.check_file_exists_exception(f)

    def manage_parameters(self):
        super().manage_parameters()

        if self.git_repo:
            BashCmd(self.rundir).run(self.git_clone_str())

        if self.ref_rundir:
            for fldr in self.ref_rundir:
                self._log(fldr, "...")
                ufiles.copy_folder_content(fldr, self.rundir, True,
                                           True, self.sym_link_big)

        if self.rundir_files:
            for f in [Path(f) for f in self.rundir_files]:
                ufiles.copy_file(f, Path(self.rundir, f.name))

        if self.tar_gz_files:
            for f in [Path(f) for f in self.tar_gz_files]:
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self.rundir)

    # ===============================PRIVATE METHODS============================
    def git_clone_str(self) -> str:
        return "git clone " + self.git_repo + " " + self.git_branch_str() + "."

    def git_branch_str(self) -> str:
        return f"-b {self.git_branch}" if self.git_branch else ""
