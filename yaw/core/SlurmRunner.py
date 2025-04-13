from .AbstractSlurmRunner import AbstractSlurmRunner
from utils import *

class SlurmRunner(AbstractSlurmRunner):

    def run(self):
        info("Generatig SLURM script....")
        generate_slurm_script(
            f_path=Path(self._gp("rundir"), self._gp("slr_wrapper_name")), 
            log_file=self.get_log_path(),
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
                f"source {self.env_file}" if self.env_file else "",
                f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            ]
        )
        if self.dry:
            print("DRY MODE: Not executing anything!")
        else:
            execute_slurm_script(self.wrapper_name, None, self.rundir)

