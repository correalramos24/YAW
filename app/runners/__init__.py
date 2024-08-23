

from .slurm_runner import slurmRunner
from .xios_compiler import xiosCompiler
from .bash_runner import bashRunner
from .abstract_runner import AbstractRunner


runners : dict[str, AbstractRunner]= {
    "slurm_runner": slurmRunner,
    "xios_compile": xiosCompiler,
    "bash_runner": bashRunner
}
