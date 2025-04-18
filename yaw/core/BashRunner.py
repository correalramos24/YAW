
from .AbstractRunner import AbstractRunner
from pathlib import Path
from utils import *
import tarfile

class BashRunner(AbstractRunner):
    """
    Run scripts or commands in bash.
    """
    @classmethod
    def get_runner_type(cls) -> str:
        return "BashRunner"

    @classmethod
    def get_params_dict(cls):
        aux = super().get_params_dict()
        aux.update({
            "wrapper" : (None, "execute your command with a wrapper", "O"),
            "bash_cmd": (None, "Script to execute (./s.sh) or command (ls)", "R"),
            "args" : (None, "Script arguments", "O"),
            "script_name" : ("yaw_wrapper.sh", "Bash script name", "O"),
            "track_env" : ("env.log", "File name to store the env of a run", "O"),
            "ref_rundir": (None, "Reference rundir to use, (copy all to rundir)", "O"),
            "rundir_files": (None, "List of files to copy to the rundir", "O"),
            "tar_gz_files": (None, "List of tar.gz. files to uncomp. to then rundir", "O"),
            "git_repo": (None, "Git repository to fill the rundir", "O"),
            "git_branch": (None, "Git branch for git_repo", "O"),
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
        
        
    def manage_multi_recipie(self):
        if not self.all_same_rundir:
            self.runner_print("No need to tune parameters for multirecipie!")
        elif self._gp("create_dir"):
            self.runner_print("Tunning parameters for multirecipie!")
            self._sp("rundir", Path(self._gp("rundir"), self.recipie_name()))
            self.runner_info("Update rundir with recipie name", self._gp("rundir"))
        else:
            self.runner_print("Need to tune parameters for multirecipie!")
            self._sp("script_name", f"{self.recipie_name()}_{self._gp('script_name')}")
            self._sp("track_env", f"{self.recipie_name()}_{self._gp('track_env')}")
            if self._gp('log_name') is not None:
                self._sp("log_name", f"{self.recipie_name()}_{self._gp('log_name')}")

    def run(self):
        #1. Generate bash script:
        wrapper_cmd = f"{self._gp("wrapper")} " if self._gp("wrapper") else ""
        args_str = self._gp("args") if self._gp("args") else ""
        generate_bash_script(Path(self._gp("rundir"), self._gp("script_name")),[
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            f"{wrapper_cmd}{self._gp("bash_cmd")} {args_str}"
            ]
        )
        #2. Execute:
        if self._gp("dry"): 
            print("DRY MODE: Not executing anything!")
            self.runner_result = "DRY"
        else:
            r = self.runner_result = execute_script( 
                script = self._gp("script_name"), 
                args = self._gp("args"),
                rundir = self._gp("rundir"),
                log_file = self.get_log_path()
            )
            if not r: self.runner_status = "OK"
            else: self.runner_status = "Return code !=0"
      

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        ret = super().get_multi_value_params()
        ret.add("rundir_files")
        ret.add("tar_gz_files")
        return ret
         
    #===============================PRIVATE METHODS=============================
    def git_clone_str(self) -> str:
        return "git clone " + self._gp("git_repo") + " " + self.git_branch_str() + "."
    
    def git_branch_str(self) -> str:
        return f"-b {self._gp('git_branch')}" if self._gp("git_branch") else ""
    