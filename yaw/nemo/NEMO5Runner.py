from nemo import AbstractNemo5Runner
from utils import *


class NEMO5Runner(AbstractNemo5Runner):
   
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "nemo5_run_cfg" : (None, "CFG to be executed", "R"),
            "nemo5_inputs" : (None, "NEMO5 Inputs (list of fldrs or fldr)", "R")
        })
        return aux
    
    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return super().get_multi_value_params().union({"nemo5_inputs"})
        
    def manage_parameters(self):
        super().manage_parameters()
        
                                
        # COPY CFG FOLDER
        self.runner_print(f"NEMO using cfg: {self._gp('nemo5_run_cfg')}")
        cfg_fldr  = Path(self._gp("nemo5_root"), "cfgs", self._gp("nemo5_run_cfg"))
        
        utils_files.copy_folder(
            Path(cfg_fldr, "EXP00"), 
            Path(self._gp("rundir")), 
            True, False) # Folder will be created by inheritance.

        self.__manage_inputs()
        self.update_namelist()
        

    def run(self):
        script_name = self._gp("script_name")
        script_path = Path(self._gp("rundir"), script_name)
        self.runner_info(f"Generating NEMO5 SLURM script ({script_name})...")
        
        launch_cmd = "srun"
        if self._gp("tasks"):
            info(f"Overriding number of tasks to {self._gp('tasks')}")
            launch_cmd += f" -n {self._gp('tasks')}"
        launch_cmd += " nemo"
        
        generate_slurm_script(
            f_path=script_path, log_file=self._gp("log_name"),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
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

    def __manage_inputs(self):
        inputs = self._gp("nemo5_inputs")
        if is_a_list(inputs):
            for input in inputs:
                self.runner_info(f"Using inputs from {input}...")
                utils_files.check_path_exists_exception(input)
                utils_files.gen_symlink_from_folder(
                    Path(input),
                    Path(self._gp("rundir")), True)
        else:
            self.runner_info(f"Using inputs from {inputs}...")
            utils_files.check_path_exists_exception(inputs)
            utils_files.gen_symlink_from_folder(
                Path(inputs),
                Path(self._gp("rundir")), True)

    