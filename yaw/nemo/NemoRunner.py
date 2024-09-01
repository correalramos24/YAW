from core import SlurmRunner
from utils import *
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class NemoRunner(SlurmRunner):
    type: str = "NemoRunner"
    nemo_root : Path = None
    nemo_cfg : str = None
    WRAPPER_NAME="nemo.slurm"
    
    # Optional, initialized to some arbitrary value:
    steps : int = 10
    # CONSTANTS:
    PATH_TO_NEMO=Path('BLD','bin','nemo.exe')

    def __post_init__(self):
        self.req_param = deepcopy(self.req_param)
        self.req_param.extend(["nemo_root", "nemo_cfg"])
        super().__post_init__()
        self.nemo_root = Path(self.nemo_root)

    def manage_parameters(self):
        super().manage_parameters()
        # 1. Check file presence:
        bin_nemo = Path(self.nemo_root, 'cfgs', self.nemo_cfg, self.PATH_TO_NEMO)
        check_file_exists_exception(bin_nemo)
        if self.env_file: 
            check_file_exists_exception(self.env_file)
        # 2. Copy them to the rundir:
        copy_file(bin_nemo, Path(self.rundir, 'nemo.exe'))
        
    def _inflate_runner(self):
        slurm_directives = {k : v for k, v in self.__dict__.items() 
                            if k.startswith("slurm_") and v }
        generate_slurm_script(Path(self.rundir, self.WRAPPER_NAME),
                              slurm_directives,
                              [
                "# loading and saving the source:",
                f"source {self.env_file}" if self.env_file else "",
                "printenv &> env.log",
                "# Editing namelist parameters:",
                f"sed -i 's/nn_stock=.*/nn_stock=-1/' \"namelist_cfg\"",
                f"sed -i 's/[[:space:]]*nn_stock[[:space:]]*=[[:space:]]*.*/nn_stock=-1/' \"namelist_cfg\"",
                f"sed -i \"s/nn_itend[ \\t]*=.*/nn_itend={self.steps}/\" namelist_cfg",
                "# Running the model:",
                f"{self.bash_cmd} $@"
            ]
        )


    @classmethod
    def _inflate_yaml_template_info(cls):
        parameters_info = SlurmRunner._inflate_yaml_template_info()
        parameters_info.extend([
            ("nemo_root", "nemo installation root"),
            ("nemo_cfg" ,  "nemo cfg to be executed"),
            ("steps" , "model steps to be executed (10 by default)")
        ])
        return parameters_info

