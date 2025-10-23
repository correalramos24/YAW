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
        
        utils_files.copy_file(Path(self._gp("xios_path")), self._gp("rundir"))
        
        if self._gp("slurm_nodes") != self._gp("xios_nodes") + self._gp("nemo_nodes"):
            raise Exception("Inconsisten number of nodes!")        

    def run(self):
        mpi_lib = self._gp("mpi_lib")        
        if mpi_lib == "OPEN-MPI": self.__run_ompi()
        elif mpi_lib == "INTEL-MPI": self.__run_impi()
        else: raise Exception("Invalid MPI LIB", mpi_lib)
    
    def __run_impi(self):
        raise Exception("Not implemented yet!")
    
    def __run_ompi(self):
        script_name = self._gp("script_name")
        script_path = Path(self._gp("rundir"), script_name)
        
        env=f"NEMO_NODES={self._gp("nemo_nodes")},NEMO_TPN={self._gp("nemo_tpn")},"
        env+=f"XIOS_NODES={self._gp("xios_nodes")},XIOS_TPN={self._gp("xios_tpn")}"
        self.runner_info(f"Generating NEMO5 SLURM script ({script_name})...")
        generate_slurm_script(
            f_path=script_path, log_file=self._gp("log_name"),
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
            f"source {self._gp("env_file")}" if self._gp("env_file") else "",
            "export SLURM_CPU_BIND=none",
            f"printenv &> {self._gp("track_env")}" if self._gp("track_env") else "",
            "# RUN XIOS+NEMO!",
            "mpirun -rf $RF_NAME --display-allocation --display-map -n $NEMO_TASKS ./nemo : -n $XIOS_TASKS ./xios_server.exe"
            ]
        )
        self.runner_info("DONE!")
        if self._gp("dry"): 
            self.runner_print("DRY MODE: Not executing anything!")
            self.runner_print("Required env to execute this runner:")
            self.runner_print(env)
            self.set_result(0, "DRY EXECUTION!")
        else:
            execute_slurm_script(script_path, None, self._gp("rundir"), env)
            self.set_result(0, "SUBMITTED")

    def __run_impi(self):
        pass