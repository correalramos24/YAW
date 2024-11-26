from core import SlurmRunner
from utils import *
from dataclasses import dataclass

@dataclass
class RunNemo(SlurmRunner):
    type: str = "RunNemo"
    nemo_root : Path = None
    nemo_cfg : str = None
    WRAPPER_NAME="nemo.slurm"
    steps : int = 10
    PATH_TO_NEMO=Path('BLD','bin','nemo.exe')

    def __post_init__(self):
        super().__post_init__()
        self.nemo_root = Path(self.nemo_root)

    def manage_parameters(self):
        super().manage_parameters()
        # COPY NEMO BIN TO RUNDIR:
        bin_nemo = Path(self.nemo_root, 'cfgs', self.nemo_cfg, self.PATH_TO_NEMO)
        check_file_exists_exception(bin_nemo)
        copy_file(bin_nemo, Path(self.rundir, 'nemo.exe'))

    def inflate_runner(self):
        generate_slurm_script(Path(self.rundir, self.WRAPPER_NAME),
            self.log_name, self._get_slurm_directives(), 
            [
                "# loading and saving the source:",
                f"source {self.env_file}" if self.env_file else "",
                "printenv &> env.log",
                "# Editing namelist parameters:",
                f"sed -i 's/nn_stock=.*/nn_stock=-1/' \"namelist_cfg\"",
                f"sed -i 's/[[:space:]]*nn_stock[[:space:]]*=[[:space:]]*.*/nn_stock=-1/' \"namelist_cfg\"",
                f"sed -i \"s/nn_itend[ \\t]*=.*/nn_itend={self.steps}/\" namelist_cfg",
                "# Running the model:",
                f"srun ./nemo.exe $@"
            ]
        )
    # PARAMETER METHODS:
    @classmethod
    def get_required_params(self) -> list[str]:
        return super().get_required_params() + ["nemo_root", "nemo_cfg"]
    
    @classmethod
    def _inflate_yaml_template_info(cls):
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "NEMO PARAMETERS"),
            ("nemo_root", "nemo installation root"),
            ("nemo_cfg" ,  "nemo cfg to be executed"),
            ("steps" , "model steps to be executed (10 by default)")
        ])
        return parameters_info