
from .AbstractRunner import AbstractRunner
from pathlib import Path
from utils import *
import tarfile

class BashRunner(AbstractRunner):
    """
    Run scripts or commands in bash.
    """

    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "bash_cmd": (None, "Script to execute (./s.sh) or command (ls)", "R"),
            "args" : (None, "Script arguments", "O"),
            "wrapper" : (None, "execute your command with a wrapper", "O"),
            "script_name" : ("yaw_wrapper.sh", "Bash script name", "O"),
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
        self.wrapper_script = Path(self._gp("rundir"), self._gp("script_name"))
        
    def manage_multi_recipie(self):
        if self._gp("same_rundir"):
            self.runner_info("Using same rundir for all recipie(s)")
            self._sp("script_name", f"{self.recipie_name()}_{self._gp('script_name')}")
            if self._gp('trak_env') is not None:
                self._sp("track_env", f"{self.recipie_name()}_{self._gp('track_env')}")
            if self._gp('log_name') is not None:
                self._sp("log_name", f"{self.recipie_name()}_{self._gp('log_name')}")
            self.runner_info("Updated some params. with", self._gp("rundir"))
        else:
            self.runner_info("Using different rundirs for each recipie(s)")
            self._sp("rundir", Path(self._gp("rundir"), self.recipie_name()))
            self.runner_info("Updated rundir to", self._gp("rundir"))
            
    def run(self):
        generate_bash_script(self.wrapper_script,[
            self._get_env_str(),
            self._get_env_trk_str(),
            self._get_cmd_str(),
        ])
        self.runner_info("Generated bash script:", self._gp("script_name"))

        if self._gp("dry"): 
            self.runner_print("DRY MODE: Not executing anything!")
            self.set_runner_result(0, "DRY RUN")
        else:
            r = self.runner_result = execute_script( 
                script = self._gp("script_name"), args = self._gp("args"), 
                rundir = self._gp("rundir"), log_file = self.log_path
            )
            if not r: self.set_runner_result(0, "OK")
            else: self.set_runner_result(-1, "Return code !=0")

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return super().get_multi_value_params().union({"rundir_files", "tar_gz_files"})
         
    #===============================PRIVATE METHODS=============================
    def git_clone_str(self) -> str:
        return "git clone " + self._gp("git_repo") + " " + self.git_branch_str() + "."
    
    def git_branch_str(self) -> str:
        return f"-b {self._gp('git_branch')}" if self._gp("git_branch") else ""
    
    def _get_env_str(self) -> str:
        if self._gp("env_file"): return f"source {self._gp('env_file')}"
        else: return ""

    def _get_env_trk_str(self) -> str:
        if self._gp("track_env"): return f"printenv &> {self._gp('track_env')}"
        else: return ""

    def _get_cmd_str(self) -> str:
        """
        Get the command string to execute.
        """
        ret = ""
        if self._gp("wrapper"):
            ret += f"{self._gp('wrapper')} "
        ret += self._gp("bash_cmd")
        if self._gp("args"):
            ret += " " + "".join(self._gp("args"))
        return ret
