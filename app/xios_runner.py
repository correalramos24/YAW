
from abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from utils import *


@dataclass
class xiosCompiler(AbstractRunner):
    xios_root: Path
    arch_name : str
    env_file : Path
    c_compiler : str = None
    f_compiler : str = None
    linker : str = None
    make_xios_flags: str = None
    make_jobs : int  = 1
    generate_arch : bool = True
    submit_script : bool = False
    svn_repo : str = None
    svn_rev  : int = None

    req_args_msg = "xios_root and arch_name are required parameters!"

    def check_parameters(self):
        if self.xios_root is None or self.arch_name is None:
            print(self.req_args_msg)
            exit(1)

        if self.svn_repo is None and not self.xios_root:
            print("Either select a xios_root or provide a svn repo! Check YAML file")
            exit(1)

        if self.generate_arch:
            if (self.c_compiler is None) or (self.f_compiler is None) or (self.linker is None):
                print("If generate_arch is enable, you need to provide c_compiler, f_compiler and linker, check YAML file")
                exit(1)

        if self.env_file is None:
            print("WARNING! You're running with a default environment, check YAML file")
        else:
            check_file_exists(self.env_file)

    def run(self):
        # 1. Download XIOS / Check xios_root 
        if self.svn_repo:
            print(f"Downloading XIOS from {self.svn_repo} to {self.xios_root}")
            if self.svn_rev is not None:
                print(f"Using rev", self.svn_rev)

        else:
            check_path_exists(self.xios_root)
            check_file_exists(Path(self.xios_root, "make_xios"))

        # 2. Generate arch file ?
        if self.generate_arch:
            self.generate_arch_file()
        else:
            check_file_exists(Path(self.xios_root, "arch", "arch-"+self.arch_name+".fcm"))

        # 3. Run make_xios!

        # TODO: Find a way to go to xios_root ...
        # TODO: Find a way to load the env file ...
        if self.submit_script:
            print("Run using srun!")
        else:
            print("Compiling using bash!")
    
    def generate_arch_file(self):
        print("Generating arch", self.arch_name)
