from core import AbstractSlurmRunner
from utils import *


class NEMO5Runner(AbstractSlurmRunner):
   
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "slurm_nodes": (None, "Number of nodes to use", "O"),
            "nemo5_root" : (None, "Root of the nemo source.", "R"),
            "nemo5_run_cfg" : (None, "CFG to be executed", "O"),
            "nemo5_inputs" : (None, "Inputs to be copied to the rundir", "O"),
            "nemo5_test_cfg" : (None, "CFG to be executed from /tests", "O"),
            "nemo5_resolution" : (None, f"Set resolution to be used: {cls.__supported_resolutions()}", "O"),
            "nemo5_timesteps" : (0, "Simulation timesteps. Namelist default if 0", "O"),
            "nemo5_jpni" : (-1, "JPNI file to be used", "O"),
            "nemo5_jpnj" : (-1, "JPNJ file to be used", "O"),
            "nemo5_cpn" : (0, "Number of cores per node of the machine", "O"),
            "nemo5_tiling_i" : (99999, "Set tiling i", "O"),
            "nemo5_tiling_j" : (99999, "Set tiling j", "O"),
            "tasks" : (None, "Number of tasks to be used", "S"),
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()            
        
        # Check if slurm_nodes is set or nemo5_jni/jpnj is not -1:
        if (self._gp("slurm_nodes") is None and 
        (self._gp("nemo5_jpni") != -1 or self._gp("nemo5_jpnj") != -1) and 
        self._gp("nemo5_cpn") == 0):
            raise Exception("Either slurm_nodes must be set or nemo5_jpni/jpnj and nemo5_cpn must be set!")

        if self._gp("slurm_nodes") is None:
            self._sp("tasks", self._gp("nemo5_jpni") * self._gp("nemo5_jpnj"))
            slurm_nodes = (self._gp('tasks') + self._gp('nemo5_cpn') - 1) // self._gp('nemo5_cpn')
            self._sp("slurm_nodes", slurm_nodes)
            info(f"Setting execution to {self._gp('tasks')} using {self._gp('slurm_nodes')} ({self._gp('nemo5_cpn')} cores per node).")
        
        if self._gp("nemo5_inputs") is not None:
            utils_files.check_path_exists_exception(self._gp("nemo5_inputs"))
                                
        # COPY CFG FOLDER
        if self._gp("nemo5_run_cfg") is not None:
            self.runner_print(f"NEMO using cfg: {self._gp('nemo5_run_cfg')}")
            cfg_fldr  = Path(self._gp("nemo5_root"), "cfgs", self._gp("nemo5_run_cfg"))
        elif self._gp("nemo5_test_cfg") is not None:
            if self._gp("nemo5_resolution"):
                raise Exception("nemo5_resolution must not be set when using nemo5_test_cfg!")
            self.runner_print(f"NEMO using test cfg: {self._gp('nemo5_test_cfg')}")
            cfg_fldr = Path(self._gp("nemo5_root"), "tests", self._gp("nemo5_test_cfg"))
        else:
            raise Exception("Either nemo5_run_cfg or nemo5_test_cfg must be set!")
        
        utils_files.copy_folder(Path(cfg_fldr, "EXP00"), 
                                Path(self._gp("rundir")), 
                                True, False) # Folder will be created by inheritance.

        # SET INPUTS:
        if self._gp("nemo5_test_cfg"):
            aux_nml = f"namelist_cfg_{self._gp("nemo5_resolution")}_like"
            utils_files.gen_symlink(Path(self._gp("rundir"), aux_nml),
                                Path(self._gp("rundir"), "namelist_cfg"))

        if self._gp("nemo5_run_cfg"):
            self.runner_info(f"Using inputs from {self._gp("nemo5_inputs")}")
            utils_files.gen_symlink_from_folder(Path(self._gp("nemo5_inputs")),
                                                Path(self._gp("rundir")), True)
            
            
        # SET NAMELISTS PARAMETERS: TIMESTEPS
        nml = Path(self._gp("rundir"), "namelist_cfg")
        if not os.access(nml, os.W_OK):
            os.chmod(nml, 0o644)
            
        if self._gp("nemo5_timesteps") > 0:
            utils_fortran.update_f90nml_key_value(nml, "namrun", "nn_itend", self._gp("nemo5_timesteps"))

        # SET NAMELISTS PARAMETERS: TILING
        if self._gp("nemo5_tiling_i") != 99999 or self._gp("nemo5_tiling_j") != 99999:
            info(f"Adding tiling values {self._gp('nemo5_tiling_i')}x{self._gp('nemo5_tiling_j')}")
            utils_fortran.add_f90nml(nml, "namtile", {
            'ln_tile': True,
            'nn_ltile_i': self._gp("nemo5_tiling_i"),
            'nn_ltile_j': self._gp("nemo5_tiling_j")
            })    
        
        if self._gp("nemo5_jpni") != -1:
            info(f"Setting jpni value to {self._gp('nemo5_jpni')}")
            utils_fortran.update_f90nml_key_value(nml, "nammpp", "jpni", self._gp("nemo5_jpni"))
        if self._gp("nemo5_jpnj") != -1:
            info(f"Setting jpnj value to {self._gp('nemo5_jpnj')}")
            utils_fortran.update_f90nml_key_value(nml, "nammpp", "jpnj", self._gp("nemo5_jpnj"))
        

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

    
    @staticmethod
    def __supported_resolutions() -> list[str]:
        return ["orca1", "orca025", "orca12"]

