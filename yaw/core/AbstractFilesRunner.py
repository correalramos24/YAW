from .AbstractRunner import AbstractRunner
from pathlib import Path
from utils import *
import tarfile


class AbstractFilesRunner(AbstractRunner):
    """
    Abstract class for runners that manage files.
    It provides methods to manage input files, output files, and other file-related tasks.
    """

    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "ref_rundir": (None, "Reference rundir to use, (copy all to rundir)", "O"),
            "rundir_files": (None, "List of files to copy to the rundir", "O"),
            "tar_gz_files": (None, "List of tar.gz. files to uncomp. to then rundir", "O"),
            "git_repo": (None, "Git repository to fill the rundir", "O"),
            "git_branch": (None, "Git branch for git_repo", "O"),
            "symlink_big_f" : (True, "Symlink big files from ref_rundir instead of copying them", "O"),
        })
        return aux

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return super().get_multi_value_params().union({
            "ref_rundir", "rundir_files", "tar_gz_files"}
        )

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
                utils_files.check_path_exists_exception(fldr)

        if self.tar_gz_files:
            for f in [Path(f) for f in self.tar_gz_files]:
                check_file_exists_exception(f)

    def manage_parameters(self):
        super().manage_parameters()

        if self.git_repo: execute_command(self.git_clone_str(), self.rundir)
        
        if self.ref_rundir:
            for fldr in self.ref_rundir:
                self._log(fldr, "...")
                copy_folder_content(fldr, self.rundir, True, True,
                                    self.symlink_big_f)
        
        if self.rundir_files:
            for f in [Path(f) for f in self.rundir_files]:
                copy_file(f, Path(self.rundir, f.name))
        
        if self.tar_gz_files:
            for f in [Path(f) for f in self.tar_gz_files]:
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self.rundir)

    #===============================PRIVATE METHODS=============================
    def git_clone_str(self) -> str:
        return "git clone " + self.git_repo + " " + self.git_branch_str() + "."
    
    def git_branch_str(self) -> str:
        return f"-b {self.git_branch}" if self.git_branch else ""