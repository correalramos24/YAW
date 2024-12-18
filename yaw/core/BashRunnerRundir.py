from .BashRunner import BashRunner
from utils import *

import tarfile


class BashRunnerRundir(BashRunner):
    """
    Bash runner with support for rundir setup.
    """

    def __init__(self, **parameters):
        super().__init__(**parameters)
        self.rundir         = self._get_path_parameter("rundir")
        self.ref_rundir     = self._get_path_parameter("ref_rundir")
        self.git_repo       = self._get_parameter_value("git_repo")
        self.git_branch     = self._get_parameter_value("git_branch")
        
        self.rundir_files   = self._get_parameter_value("rundir_files")
        self.rundir_files   = [Path(f) for f in self.rundir_files] \
                                if self.rundir_files else None

        self.tar_gz_files   = self._get_parameter_value("tar_gz_files")
        self.tar_gz_files   = [Path(f) for f in self.tar_gz_files] \
                                if self.tar_gz_files else None
        
        if self.git_branch and not self.git_repo:
            raise Exception("Git branch selected but repo not selected!")


    def manage_parameters(self):
        super().manage_parameters()
        if self.ref_rundir:
            copy_folder(self.ref_rundir, self.rundir, True)
        if self.git_repo:
            branch = f"-b {self.git_branch}" if self.git_branch else ""
            info("Cloning repo", self.git_repo, branch)
            execute_command(f"git clone {self.git_repo} {branch}", self.rundir)
        if self.rundir_files:
            for f in self.rundir_files:
                copy_file(f, Path(self.rundir, f.name))
        if self.tar_gz_files:
            for f in self.tar_gz_files:
                check_file_exists_exception(f)
                with tarfile.open(f, "r:gz") as tar:
                    tar.extractall(path=self.rundir)

    #===============================PARAMETER METHODS===========================
    @classmethod
    def get_runner_type(cls) -> str:
        return "BashRunnerRundir"
    
    @classmethod
    def get_parameters(cls) -> list[str]:
        return super().get_parameters() + \
            ["ref_rundir", "rundir_files", "tar_gz_files", 
             "git_repo", "git_branch"]
    
    @classmethod
    def get_required_params(self):
        return super().get_required_params() + ["rundir"]
    
    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        ret = super().get_multi_value_params()
        ret.add("rundir_files")
        ret.add("tar_gz_files")
        return ret

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[str]:
        params_info = super()._inflate_yaml_template_info()
        params_info.extend([
            ("comment", "RUNDIR PARAMETERS"),
            ("ref_rundir", "Reference rundir to use, (copy all to rundir)"),
            ("rundir_files", "List of files to copy to the rundir"),
            ("tar_gz_files", "List of tar.gz. files to uncomp. to then rundir"),
            ("git_repo", "Git repository to fill the rundir"),
            ("git_branch", "Git branch for git_repo")
        ])
        return params_info