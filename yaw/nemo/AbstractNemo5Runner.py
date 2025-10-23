from yaw.core import AbstractSlurmRunner

from utils import utils_fortran as uf
from utils import utils_files as ufile
from pathlib import Path

class AbstractNemo5Runner(AbstractSlurmRunner):
    @classmethod
    def get_tmp_params(cls):
        aux = super().get_tmp_params()
        aux.update({
            "slurm_nodes": (None, "Number of nodes to use", "O"),
            "nemo5_root" : (None, "Root of the nemo source.", "R"),
            "nemo5_timesteps" : (0, "Simulation timesteps. Namelist default if 0", "O"),
            "nemo5_jpni" : (None, "JPNI file to be used.", "O"),
            "nemo5_jpnj" : (None, "JPNJ file to be used.", "O"),
            "nemo5_cpn" : (None, "Number of cores per node of the machine", "O"),
            "nemo5_tiling_i" : (None, "Set tiling i", "O"),
            "nemo5_tiling_j" : (None, "Set tiling j", "O"),
            "nemo5_nncomm" : (None, "Set nn_comm parameter, default 1", "O"),
            "tasks" : (None, "Number of tasks to be used", "S"),
            "ld_preload"  : (None, "Add a dynamic librarie before nemo", "O")
        })
        return aux
    
    def manage_parameters(self):
        super().manage_parameters()
        
        ufile.check_path_exists_exception(self.nemo5_root)
        
        if self.slurm_nodes is None:
            tasks, nodes = self.__compute_nodes_from_jpni_jpnj()
            self.slurm_tasks = tasks
            self.slurm_nodes = nodes
            self.runner_info(f"Executin NEMO5 with {tasks} @ {nodes}.")
    
    def update_namelist(self):
        """Set namelist values according runner params"""
        self.__set_jpni_jpnj()
        self.__set_timesteps()
        self.__set_tilling()
        self.__set_nncom()
    
    #===============================PRIVATE METHODS=============================
    def __compute_nodes_from_jpni_jpnj(self):
        """
        Compute the number of nodes from jpni and jpnj.
        """
        jpni= self.nemo5_jpni
        jpnj= self.nemo5_jpnj
        cpn = self.nemo5_cpn
        
        if not jpni or not jpnj or not cpn:
            raise Exception("nemo5_jpni/_jpnj/_cpn or slurm_nodes must be set!")
        
        if cpn <= 0:
            raise Exception("nemo5_cpn must be greater than 0!")
        
        if jpni <= 0 or jpnj <= 0:
            raise Exception("nemo5_jpni and nemo5_jpnj must be greater than 0!")
        
        tasks = jpni * jpnj
        slurm_nodes = (tasks + cpn - 1) // cpn
        return tasks, slurm_nodes
    
    def with_nml(func):
        def wrapper(self, *args, **kwargs):
            nml = Path(self.rundir, "namelist_cfg")
            return func(self, nml, *args, **kwargs)
        return wrapper
    
    @with_nml
    def __set_timesteps(self, nml):
        ts = self.nemo5_timesteps
        if ts > 0:
            uf.update_f90nml_key_value(nml, "namrun", "nn_itend", ts)
        else:
            raise Exception("nemo5_timesteps was negative!")
    
    @with_nml
    def __set_jpni_jpnj(self, nml):
        if self.nemo5_jpni:
            self.runner_info(f"Setting jpni value to {self.nemo5_jpni}")
            uf.update_f90nml_key_value(nml, "nammpp", "jpni", self.nemo5_jpni)
        if self.nemo5_jpnj:
            self.runner_info(f"Setting jpnj value to {self.nemo5_jpnj}")
            uf.update_f90nml_key_value(nml, "nammpp", "jpnj", self.nemo5_jpnj)
    
    @with_nml
    def __set_tilling(self, nml):
        if self.nemo5_tiling_i or self.nemo5_tiling_j:
            self.runner_info(f"Adding tiling values {self.nemo5_tiling_i}x{self.nemo5_tiling_j}")
            uf.add_f90nml(nml, "namtile", {
                'ln_tile': True,
                'nn_ltile_i': self.nemo5_tiling_i,
                'nn_ltile_j': self.nemo5_tiling_j
            })
    
    @with_nml
    def __set_nncom(self, nml):
        nncomm = self._gp('nemo5_nncomm')
        if nncomm:
            self.runner_info(f"Setting nn_comm to {nncomm}")
            uf.update_f90nml_key_value(nml, "nammpp", "nn_comm", nncomm)
    
