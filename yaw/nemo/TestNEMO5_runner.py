from nemo import AbstractNemo5Runner
from utils import *


class TestNEMO5Runner(AbstractNemo5Runner):
   
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "nemo5_test_cfg" : (None, "CFG to be executed from /tests", "R"),
            "nemo5_resolution" : (None, f"Resolution to be used: {cls.__supported_resolutions()}", "R")
        })
        return aux
    
    @staticmethod
    def __supported_resolutions() -> list[str]:
        return ["orca1", "orca025", "orca12"]
    
    def manage_parameters(self):
        super().manage_parameters()            

        cfg = self._gp('nemo5_test_cfg')
        rundir = self._gp("rundir")
        self.runner_print(f"NEMO using test cfg: {cfg}")
        
        utils_files.copy_folder(
            Path(self._gp("nemo5_root"), "tests", cfg, "EXP00"), 
            Path(rundir), True, False) # Folder will be created by inheritance.

        utils_files.gen_symlink(
            Path(rundir, f"namelist_cfg_{self._gp("nemo5_resolution")}_like"), 
            Path(rundir, "namelist_cfg"))
            
        self.update_namelist()

    def run(self):
        script_name = self._gp("script_name")
        script_path = Path(self._gp("rundir"), script_name)
        self.runner_info(f"Generating NEMO5 SLURM script ({script_name})...")
        
        launch_cmd = "srun"
        if self._gp("tasks"):
            info(f"Overriding number of tasks to {self._gp('tasks')}")
            launch_cmd += f" -n {self._gp('tasks')}"
        launch_cmd += " --cpu-bind=cores nemo"
        
        preload_str = ""
        if self._gp("ld_preload") is not None:
            print("Using ld_preload", self._gp("ld_preload"), "...")
            preload_str += f"export LD_PRELOAD={self._gp("ld_preload")}\n"
            preload_str += "export PAPI_LIST=\"PAPI_TOT_CYC,PAPI_L3_TCM\""

        generate_slurm_script(
            f_path=script_path, log_file=self._gp("log_name"),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            "export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            preload_str,
            launch_cmd,
            ]
        )
        self.runner_info("DONE!")
        if self._gp("dry"): 
            self.runner_print("DRY MODE: Not executing anything!")
            self.set_result(0, "DRY EXECUTION!")
        else:
            execute_slurm_script(script_path, None, self._gp("rundir"))
            self.set_result(0, "SUBMITTED")

    

