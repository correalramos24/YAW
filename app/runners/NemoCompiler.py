from . import AbstractRunner
from .BashRunner import BashRunner
from dataclasses import dataclass
from app.utils import *
from pathlib import Path

@dataclass
class NemoCompiler(AbstractRunner):
    type : str = "NemoCompiler"
    # CFG Setup:
    arch_name : str = None
    cfg_name  : str = None
    ref_cfg : str = None
    modules : str = None
    add_keys : str = None
    del_keys : str = None
    make_jobs : int = 8

    # Generate arch file:
    generate_arch : bool = False
    cpp_compiler : str = None
    c_compiler : str = None
    f_compiler : str = None
    linker : str = None
    f_flags : str = None
    ld_flags : str = None
    fpp_flags : str = None

    def __post_init__(self):
        self.req_param.extend(["cfg_name", "ref_cfg"])
        super().__post_init__()
        if self.generate_arch:
           # CHECK REQUIRED THEN
           pass


    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        parameters_info = super()._inflate_yaml_template_info()
        parameters_info.extend([
            ("comment", "CFG PARAMETERS"),
            ("arch_name", "Arch name to use in the compilation or to generate"),
            ("cfg_name", "CFG for the compilation"),
            ("ref_cfg", "Reference CFG for the compilation"),
            ("modules", "Modules to use in the compilation"),
            ("add_keys", "Add keys to the compilation"),
            ("del_keys", "Delete keys from the compilation"),
            ("comment", "GENERATE ARCH_FILE only if generate_arch is True"),
            ("generate_arch", "bool"),
            ("cpp_compiler", "C pre-processor "),
            ("c_compiler", "C compiler "),
            ("f_compiler", "Fortran compiler "),
            ("linker", "linker"),
            ("f_flags", "Flags for the fortran compiler"),
            ("ld_flags", "Flags for the linker"),
            ("fpp_flags", "Flags for the pre-processor"),
            ("comment", "MISC"),
            ("make_jobs", "Number of jobs to run"),
        ])
        return parameters_info