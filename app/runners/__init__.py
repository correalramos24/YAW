

from .slurm_runner import slurmRunner
from .xios_compiler import xiosCompiler
from .bash_runner import bashRunner
from .abstract_runner import AbstractRunner
from .nemo_runner import nemoRunner
from .multi_param import *

runners : dict[str, AbstractRunner]= {
    "bash_runner": bashRunner,
    "slurm_runner": slurmRunner,
    "nemo_runner" : nemoRunner,
    "xios_compile": xiosCompiler
}