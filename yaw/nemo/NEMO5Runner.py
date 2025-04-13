from core import SlurmRunner
from utils import *



class NEMO5Runner(SlurmRunner):
    
    @classmethod
    def get_runner_name(cls) -> str:
        return "NEMO5Runner"
    
    @classmethod
    def get_params_dict(cls):
        aux = super().get_params_dict()
        aux.update({
            "nemo5_root" : (None, "Root of the nemo source.", "R"),
            "nemo5_run_cfg" : (None, "CFG to be executed", "O"),
            "nemo5_test_cfg" : (None, "CFG to be executed from /tests", "O"),
            "nemo5_resolution" : (None, f"Set resolution to be used: {cls.__supported_resolutions()}", "R"),
            "nemo5_timesteps" : (1, "Simulation timesteps. Default 1", "O"),
            "nemo5_tiling_i" : (99999, "Set tiling i", "O"),
            "nemo5_tiling_j" : (99999, "Set tiling j", "O")
        })
        return aux

    def manage_parameters(self):
        super().manage_parameters()            
        
        # COPY CFG FOLDER
        if self.nemo_cfg is not None:
            cfg_fldr  = Path(self.nemo_root, "cfgs", self.nemo_cfg)
        elif self.nemo_test is not None:
            cfg_fldr = Path(self.nemo_root, "tests", self.nemo_test)
        else:
            raise Exception("Either nemo5_run_cfg or nemo5_test_cfg must be set!")
        
        utils_files.copy_folder(Path(cfg_fldr, "EXP00"), self.rundir, self.overwrite, False)

        # SET INPUTS:
        if self.nemo_test:
            aux_nml = f"namelist_cfg_{self.resolution}_like"
            utils_files.gen_symlink(Path(self.rundir, aux_nml),
                                Path(self.rundir, "namelist_cfg"))

        if self.nemo_cfg:
            raise Exception("NOT IMPLEMENTED YET")
        
        # SET NAMELISTS PARAMETERS: TIMESTEPS
        nml = Path(self.rundir, "namelist_cfg")
        if self.ts > 0:
            utils_fortran.update_f90nml_key_value(nml, "namrun", "nn_itend", self.ts)

        # SET NAMELISTS PARAMETERS: TILING
        info("Adding tiling values!")
        utils_fortran.add_f90nml(nml, "namtile", {
            'ln_tile': self.tiling_i != 99999 or self.tiling_j != 99999,
            'nn_ltile_i': self.tiling_i,
            'nn_ltile_j': self.tiling_j
        })
        

    def run(self):
        info("Generating NEMO5 SLURM script...")
        generate_slurm_script(Path(self.rundir, self.wrapper_name), 
                              self.log_path, self.slurm_directives,
            [
            f"source {self.env_file}" if self.env_file else "",
            "printenv &> env.log",
            "srun nemo",
            ]
        )
        info("DONE!")
        if self.dry:
            print("DRY MODE: Not executing anything!")
            return True
        else:
            execute_slurm_script(self.wrapper_name, None, self.rundir)
            return True

    
    @staticmethod
    def __supported_resolutions() -> list[str]:
        return ["ORCA1", "ORCA025", "ORCA12"]

