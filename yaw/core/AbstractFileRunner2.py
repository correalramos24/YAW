from yaw.core.AbstractRunner2 import AbstractRunner2

import utils.utils_files as ufiles
import utils.utils_bash as ubash

import tarfile
from pathlib import Path
from dataclasses import dataclass, field, fields
from abc import ABC
from typing import Optional, Any

@dataclass(kw_only=True)
class AbstractFileRunner2(AbstractRunner2, ABC):

    ref_rundir   : Optional[set[str]] = field(default=None, metadata={'kind':"O",
                                            "desc": "Reference rundir to use, (copy all to rundir)"})
    rundir_files : Optional[set[str]] = field(default=None, metadata={"kind": "O",
                                            "desc": "List of files to copy to the rundir"})
    tar_gz_files : Optional[set[str]] = field(default=None, metadata={"kind": "O",
                                            "desc": "List of tar.gz. files to uncomp. to then rundir"})
    git_repo     : Optional[str]      = field(default=None, metadata={"kind": "O",
                                            "desc": "Git repository to fill the rundir"})
    git_branch   : Optional[str]      = field(default=None, metadata={"kind": "O",
                                            "desc": "Git branch for git_repo"})
    sym_link_big : bool               = field(default=True, metadata={"kind": "O",
                                            "desc": "Symlink big files from ref_rundir instead of copying them"})

    def manage_parameters(self):
        super().manage_parameters()

        if self.git_repo: ubash.execute_command(self.git_clone_str(), self.rundir)

        if self.ref_rundir:
            for fldr in self.ref_rundir:
                self._log(fldr, "...")
                ufiles.copy_folder_content(fldr, self.rundir, True, True,
                                    self.sym_link_big)

        if self.rundir_files:
            for f in [Path(f) for f in self.rundir_files]:
                ufiles.copy_file(f, Path(self.rundir, f.name))

        if self.tar_gz_files:
            for f in [Path(f) for f in self.tar_gz_files]:
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self.rundir)


    # ===============================PRIVATE METHODS=============================
    def git_clone_str(self) -> str:
        return "git clone " + self.git_repo + " " + self.git_branch_str() + "."

    def git_branch_str(self) -> str:
        return f"-b {self.git_branch}" if self.git_branch else ""