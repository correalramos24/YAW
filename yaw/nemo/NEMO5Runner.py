from core import SlurmRunner
from utils import *



class NEMO5Runner(SlurmRunner):
    def __init__(self, **parameters):
        super().__init__(**parameters)
        self.nemo_root = self._get_parameter_value("nemo5_root")
        self.nemo_cfg  : Path = self._get_parameter_value("nemo5_run_cfg", None)
        self.nemo_test : Path = self._get_parameter_value("nemo5_test_cfg", None)
        self.resolution: str  = self._get_parameter_value("nemo5_resolution")        
        self.ts        : int  = self._get_parameter_value("nemo5_timesteps", 0)
        self.tiling_i  : int  = self._get_parameter_value("nemo5_tiling_i", 99999)
        self.tiling_j  : int  = self._get_parameter_value("nemo5_tiling_j", 99999)

    def manage_parameters(self):
        super().manage_parameters()            
        
        if self.nemo_cfg is not None:
            cfg_fldr  = Path(self.nemo_root, "cfgs", self.nemo_cfg)
        elif self.nemo_test is not None:
            cfg_fldr = Path(self.nemo_root, "tests", self.nemo_test)
        else:
            raise Exception("Either nemo5_run_cfg or nemo5_test_cfg must be set!")
        
        # COPY REFERENCE FOLDER:        
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

    @classmethod
    def get_runner_type(cls) -> str:
        return "NEMO5Runner"
    
    @classmethod
    def get_required_params(cls) -> list[str]:
        ret = super().get_required_params()
        return  ret + ["rundir", "nemo5_root", "nemo5_resolution"]
    
    @staticmethod
    def __supported_resolutions() -> list[str]:
        return ["ORCA1", "ORCA025", "ORCA12"]


    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "NEMO5 PARAMETERS"),
            ("nemo5_root", "Root of the nemo source."),
            ("nemo5_run_cfg", "CFG to be executed. "),
            ("nemo5_test_cfg", "CFG to be executed from /tests."),
            ("nemo5_resolutions", "Set resolution to be used"),
            ("nemo5_timesteps", "Simulation timesteps"),
            ("nemo5_tiling_i", "Set tiling i"),
            ("nemo5_tiling_j", "Set tiling j")
        ])
        return parameters_info