
from .AbstractRunner import AbstractRunner
from utils import *
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GitHelper(AbstractRunner):
    git_repo : str = None
    git_branch : str = ""

    def __post_init__(self):
        super().__post_init__()
        if self.git_branch and not self.git_repo:
            raise Exception("Git branch selected but repo not selected!")
        
    def manage_parameters(self):
        if self.git_repo:
            branch = f"-b {self.git_branch}" if self.git_branch else ""
            info("Cloning repo", self.git_repo, branch)
            execute_command(f"git clone {self.git_repo} -b {branch}")
        super().manage_parameters()

    # YAML GENERATION METHODS:
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[str]:
        params_info = super()._inflate_yaml_template_info()
        params_info.extend([
            ("git_repo", "Git repository to fill the rundir"),
            ("git_branch", "Git branch for git_repo")
        ])
        return params_info