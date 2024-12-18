from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *

class SlurmRunner(AbstractSlurmRunner):

    def run(self):
        info("Generatig SLURM script....")
        generate_slurm_script(Path(self.rundir, self.wrapper_name), 
                              self.log_path, self.slurm_directives,
            [
            f"source {self.env_file}" if self.env_file else "",
            "printenv &> env.log",
            ]
        )
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_slurm_script(self.wrapper_name, None, self.rundir)

