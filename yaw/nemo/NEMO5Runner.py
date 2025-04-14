from core import SlurmRunner
from utils import *



class NEMO5Runner(SlurmRunner):
    
    @classmethod
    def get_runner_name(cls) -> str:
        return "NEMO5Runner"
    
    @classmethod
    def get_runner_type(cls) -> str:
        return "NEMO5Runner"

    
    @classmethod
    def get_params_dict(cls):
        aux = super().get_params_dict()
        aux.update({
            "nemo5_root" : (None, "Root of the nemo source.", "R"),
            "nemo5_run_cfg" : (None, "CFG to be executed", "O"),
            "nemo5_test_cfg" : (None, "CFG to be executed from /tests", "O"),
            "nemo5_resolution" : (None, f"Set resolution to be used: {cls.__supported_resolutions()}", "R"),
            "nemo5_timesteps" : (0, "Simulation timesteps. Namelist default if 0", "O"),
            "nemo5_tiling_i" : (99999, "Set tiling i", "O"),
            "nemo5_tiling_j" : (99999, "Set tiling j", "O")
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()            
        
        # COPY CFG FOLDER
        if self._gp("nemo5_run_cfg") is not None:
            self.runner_print(f"NEMO using cfg: {self._gp('nemo5_run_cfg')}")
            cfg_fldr  = Path(self._gp("nemo5_root"), "cfgs", self._gp("nemo5_run_cfg"))
        elif self._gp("nemo5_test_cfg") is not None:
            self.runner_print(f"NEMO using test cfg: {self._gp('nemo5_test_cfg')}")
            cfg_fldr = Path(self._gp("nemo5_root"), "tests", self._gp("nemo5_test_cfg"))
        else:
            raise Exception("Either nemo5_run_cfg or nemo5_test_cfg must be set!")
        
        utils_files.copy_folder(Path(cfg_fldr, "EXP00"), 
                                self._gp("rundir"), 
                                self._gp("overwrite"), 
                                False)

        # SET INPUTS:
        if self._gp("nemo5_test_cfg"):
            aux_nml = f"namelist_cfg_{self._gp("nemo5_resolution")}_like"
            utils_files.gen_symlink(Path(self._gp("rundir"), aux_nml),
                                Path(self._gp("rundir"), "namelist_cfg"))

        if self._gp("nemo5_run_cfg"):
            raise Exception("NOT IMPLEMENTED YET")
        
        # SET NAMELISTS PARAMETERS: TIMESTEPS
        nml = Path(self._gp("rundir"), "namelist_cfg")
        if self._gp("nemo5_timesteps") > 0:
            utils_fortran.update_f90nml_key_value(nml, "namrun", "nn_itend", self._gp("nemo5_timesteps"))

        # SET NAMELISTS PARAMETERS: TILING
        info("Adding tiling values!")
        utils_fortran.add_f90nml(nml, "namtile", {
            'ln_tile': self._gp("tiling_i") != 99999 or self._gp("tiling_j") != 99999,
            'nn_ltile_i': self._gp("tiling_i"),
            'nn_ltile_j': self._gp("tiling_j")
        })
        

    def manage_multi_recipie(self):
        return 

    def run(self):
        info("Generating NEMO5 SLURM script...")
        generate_slurm_script(
            f_path=Path(self._gp("rundir"), self._gp("slr_wrapper_name")), 
            log_file=self.get_log_path(),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            "srun nemo",
            ]
        )
        info("DONE!")
        if self._gp("dry"): 
            print("DRY MODE: Not executing anything!")
            ret = "DRY EXECUTION!"
            self.runner_result = "DRY"
        else:
            execute_slurm_script(self._gp("slr_wrapper_name"), None, self._gp("rundir"))
            self.runner_result = "OK"
            self.runner_result_str = "SUBMITTED"

    
    @staticmethod
    def __supported_resolutions() -> list[str]:
        return ["orca1", "orca025", "orca12"]

