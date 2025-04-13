from .BashRunner import BashRunner
from utils import *
import tarfile


class BashRunnerRundir(BashRunner):
    """
    Bash runner with support for rundir setup.
    """

    @classmethod
    def get_runner_type(cls) -> str:
        return "BashRunnerRundir"
    
    @classmethod
    def get_params_dict(cls):
        aux =  super().get_params_dict()
        aux.update({
            "ref_rundir": (None, "Reference rundir to use, (copy all to rundir)", "O"),
            "rundir_files": (None, "List of files to copy to the rundir", "O"),
            "tar_gz_files": (None, "List of tar.gz. files to uncomp. to then rundir", "O"),
            "git_repo": (None, "Git repository to fill the rundir", "O"),
            "git_branch": (None, "Git branch for git_repo", "O"),
            "rundir": (None, "Rundir path to execute the runner.", "R"),
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()
        
        if self._gp("git_branch") and not self._gp("git_repo"):
            raise Exception("Git branch selected but repo not selected!")
        
        if self._gp("git_repo"):
            if self._gp("git_branch"):
                br_str = "Using branch: " + self._gp("git_branch")
            else:
                br_str = "Using default branch"
            info("Cloning repo", self._gp("git_repo"), br_str)
            execute_command(self.git_clone_str(), self._gp("rundir"))
        
        if self._gp("ref_rundir"):
            copy_folder(self._gp("ref_rundir"), self._gp("rundir"), True)
        
        if self._gp("rundir_files"):
            for f in [Path(f) for f in self._gp("rundir_files")]:
                copy_file(f, Path(self._gp("rundir"), f.name))
        
        if self._gp("tar_gz_files"):
            for f in [Path(f) for f in self._gp("tar_gz_files")]:
                check_file_exists_exception(f)
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self._gp("rundir"))

    #===============================PRIVATE METHODS=============================
    def git_clone_str(self) -> str:
        return "git clone " + self._gp("git_repo") + " " + self.git_branch_str() + "."
    
    def git_branch_str(self) -> str:
        return f"-b {self._gp('git_branch')}" if self._gp("git_branch") else ""
    
    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        ret = super().get_multi_value_params()
        ret.add("rundir_files")
        ret.add("tar_gz_files")
        return ret
