from core import AbstractRunner
from utils import *
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class NemoCompiler(AbstractRunner):
    type : str = "NemoCompiler"
    # CFG Setup:
    nemo_root : Path = None
    arch_name : str = None
    cfg_name  : str = None
    ref_cfg : str = None
    modules : str = None
    add_keys : str = None
    del_keys : str = None
    # Misc:
    make_jobs : int = 8
    clean_config : bool = False

    # Generate arch file:
    __generate_arch : bool = False
    cpp_compiler : str = None
    c_compiler : str = None
    f_compiler : str = None
    linker : str = None
    f_flags : str = None
    ld_flags : str = None
    fpp_flags : str = None

    def __post_init__(self):
        self.req_param = deepcopy(self.req_param)
        self.req_param.extend(["nemo_root","cfg_name", "ref_cfg"])
        super().__post_init__()
        self.__generate_arch =  self.cpp_compiler or self.c_compiler or \
                                self.f_compiler or self.linker or \
                                self.f_flags or self.ld_flags or \
                                self.fpp_flags
        self.nemo_root = Path(self.nemo_root)
        self.WRAPPER_NAME : str = f"compile_{self.cfg_name}.sh"
        if self.__generate_arch:
            pass
            #TODO: Check all required to generate arch
            #TODO: Generate arch

    def manage_parameters(self):
        super().manage_parameters()
        if self.__generate_arch:
            info("Generating arch with name", self.arch_name)

        check_file_exists_exception(Path(self.nemo_root, 'arch', 'arch-'+self.arch_name+'.fcm'))
        check_file_exists_exception(Path(self.nemo_root, "makenemo"))


    def _inflate_runner(self):
        load_env_cmd = f"source {self.env_file}" if self.env_file else ""
        compilation_str = f"./makenemo -m {self.arch_name} -r {self.ref_cfg} " \
                f"-n {self.cfg_name} -d \'{self.modules}\' " \
                f"add_key \'{self.add_keys}\' del_key \'{self.del_keys}\'"
        
        generate_bash_script(Path(self.nemo_root, self.WRAPPER_NAME),
            [
                load_env_cmd,
                "printenv &> env.log",
                compilation_str
            ]
        )

    def run(self):
        self._inflate_runner()
        if self.dry:
            info("DRY MODE! ONLY GENERATE RUNDIR")
            return
        if self.clean_config:
            self._inflate_runner()
            execute_command(f"echo \"y\" | ./makenemo -n {self.cfg_name} clean_config", self.nemo_root)

        info("Submitting compilation!")
        execute_script(self.WRAPPER_NAME, None, self.nemo_root, self.log_name)

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
            ("comment", "MISC"),
            ("make_jobs", "Number of jobs to run"),
            ("clean_config", "Force clean cfg before compiling"),
            ("comment", "Generate ARCH_FILE"),
            ("cpp_compiler", "C pre-processor "),
            ("c_compiler", "C compiler "),
            ("f_compiler", "Fortran compiler "),
            ("linker", "linker"),
            ("f_flags", "Flags for the fortran compiler"),
            ("ld_flags", "Flags for the linker"),
            ("fpp_flags", "Flags for the pre-processor"),
        ])
        parameters_info = [(key, "nemo root") if key == "rundir" else (key, value) for key, value in parameters_info]
        parameters_info = [tupla for tupla in parameters_info if tupla[0] != "ref_run_dir"]
        parameters_info = [tupla for tupla in parameters_info if tupla[0] != "rundir_files"]
        return parameters_info