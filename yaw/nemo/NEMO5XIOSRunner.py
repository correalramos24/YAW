from nemo import NEMO5Runner
from utils import *


class NEMO5XIOSRunner(NEMO5Runner):
   
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "mpi_lib"  : (None, f"Set MPI library ({cls.__supported_mpi()})", "R"),
            "nemo_nodes" : (None, "Number of nemo_nodes", "R"),
            "nemo_tpn" : (None, "Number of tasks per node of nemo", "R"),
            "xios_nodes" : (None, "Number of xios_nodes", "R"),
            "xios_tpn" : (None, "Number of tasks per node of xios", "R"),
            "xios_path": (None, "Path to XIOS binary", "R")
        })
        return aux

    @staticmethod
    def __supported_mpi() -> list[str]:
        return ["INTEL-MPI", "OPEN-MPI"]

    def manage_parameters(self):
        super().manage_parameters()
        
        utils_files.copy_file(Path(self.xios_path), self.rundir)
        
        if self.slurm_nodes != self.xios_nodes + self.nemo_nodes:
            raise Exception("Inconsisten number of nodes!")        

    def run(self):
        mpi_lib = self.mpi_lib        
        if mpi_lib == "OPEN-MPI": self.__run_ompi()
        elif mpi_lib == "INTEL-MPI": self.__run_ompi()
        else: raise Exception("Invalid MPI LIB", mpi_lib)
    
    
    def __run_ompi(self):
        script_name = self.script_name
        script_path = Path(self.rundir, script_name)
        
        env=f"NEMO_NODES={self.nemo_nodes},NEMO_TPN={self.nemo_tpn},"
        env+=f"XIOS_NODES={self.xios_nodes},XIOS_TPN={self.xios_tpn}"
        self.runner_info(f"Generating NEMO5 SLURM script ({script_name})...")
        generate_slurm_script(
            f_path=script_path, log_file=self.log_name,
            slurm_directives=self._get_slurm_directives(),
            cmds=
            [
            "# GENERATE RANK FILE:",
            "export NEMO_TASKS=$(($NEMO_NODES * $NEMO_TPN))",
            "export XIOS_TASKS=$(($XIOS_NODES * $XIOS_TPN))",
            "export RF_NAME=\"rankfile_${SLURM_JOB_ID}\"",
            "source generate_rankfile.sh",
            "rankfile_generation_logic",
            "# LOAD ENV:",
            f"source {self.env_file}" if self.env_file else "",
            "export SLURM_CPU_BIND=none",
            f"printenv &> {self.track_env}" if self.track_env else "",
            "# RUN XIOS+NEMO!",
            "mpirun -rf $RF_NAME --display-allocation --display-map -n $NEMO_TASKS ./nemo : -n $XIOS_TASKS ./xios_server.exe"
            ]
        )
        self.runner_info("DONE!")
        self.runner_print("Required env to execute this runner:")
        self.runner_print(env)
        if not self.check_dry():
            execute_slurm_script(script_path, None, self.rundir, env)
            self.set_result(0, "SUBMITTED")

    def __run_impi(self):
        pass