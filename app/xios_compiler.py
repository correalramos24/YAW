
from abstract_runner import AbstractRunner
from dataclasses import dataclass, field
from utils import *
from pathlib import Path
from os import getenv
from typing import Optional

@dataclass
class xiosCompiler(AbstractRunner):
    xios_root: Path
    bld_fldr: Path
    arch_name : str
    env_file : Path
    c_compiler : str = None
    f_compiler : str = None
    linker : str = None
    c_preproc: str = None
    f_preproc: str = None
    make_xios_flags: str = None
    make_jobs : int  = 1
    generate_arch : bool = True
    submit_script : bool = False
    svn_repo : str = None
    svn_rev  : int = None
    log_name : Optional[str] = field(default=None)

    def __post_init__(self):
        super().__post_init__()
        self.xios_root = Path(self.xios_root)
        self.bld_fldr = Path(self.bld_fldr)
        self.env_file  = Path(self.env_file)

    req_args_msg = "xios_root, bld_fldr and arch_name are required parameters!"

    def manage_parameters(self):
        # Check required parameters:
        if self.xios_root is None or self.arch_name is None or self.bld_fldr is None:
            print(self.req_args_msg)
            exit(1)
        
        # Download from svn?
        if self.svn_repo:
            print(f"Downloading XIOS from {self.svn_repo} to {self.xios_root}")
            if self.svn_rev is not None:
                print(f"Using rev", self.svn_rev)

        # Check folder & make_xios existance:
        check_path_exists_exception(self.xios_root)
        check_file_exists(Path(self.xios_root, "make_xios"))

        # Manage arch files:
        if self.generate_arch:
            if  (self.c_compiler is None) or (self.f_compiler is None) or \
                (self.linker is None) or (self.c_preproc is None) or \
                (self.f_preproc is None):
                print("If generate_arch is enable, you need to provide c_compiler, f_compiler, cpp, fpp and linker, check YAML file")
                exit(1)
            else:
                self.generate_arch_file()
        else:
            check_file_exists(Path(self.xios_root, "arch", "arch-"+self.arch_name+".fcm"))
        
        # Manage env file:
        if self.env_file is None:
            print("WARNING! You're running with a default environment, check YAML file")
        else:
            check_file_exists(self.env_file)                      

    def run(self):
        compile_str = f"./make_xios --job {self.make_jobs} --full --build-dir {self.bld_fldr} --arch {self.arch_name}"
        super().generate_bash_wrapper(Path(self.rundir, "run_wrapper.sh"), 
            [
                f"source {self.env_file}",
                "module list",
                compile_str
            ])

        print("Created run script!")
        if self.submit_script:
            print("Run using srun!")
        else:
            execute_script("./run_wrapper.sh", None, self.xios_root, self.log_name)
        
        # 4. Check if xios_sever.exe exists!
        # TODO: Complete


    def generate_arch_file(self):
        arch_root = Path(self.xios_root, "arch")
        fcm_file  = Path(arch_root,"arch-"+self.arch_name+".fcm")
        env_file  = Path(arch_root,"arch-"+self.arch_name+".env")
        path_file  = Path(arch_root,"arch-"+self.arch_name+".path")

        print("Generating", fcm_file)
        with open(fcm_file, "w") as fcm_f:
            fcm_f.write(f"""################################################################################
###################                Projet XIOS               ###################
################################################################################

%CCOMPILER      {self.c_compiler}
%FCOMPILER      {self.f_compiler}
%LINKER         {self.linker}

%BASE_CFLAGS    -ansi -w -std=c++11
%PROD_CFLAGS    -O3 -DBOOST_DISABLE_ASSERTS
%DEV_CFLAGS     -g
%DEBUG_CFLAGS   -DBZ_DEBUG -g -fno-inline

%BASE_FFLAGS    -D__NONE__
%PROD_FFLAGS    -O3
%DEV_FFLAGS     -g -O2 --traceback
%DEBUG_FFLAGS   -g --traceback

%BASE_INC       -D__NONE__
%BASE_LD        -lstdc++

%CPP            {self.c_preproc}
%FPP            {self.f_preproc}
%MAKE           gmake

""")
        print("Generating", env_file)
        
        execute_command(f"grep 'module' {self.env_file} > {env_file}", arch_root)
        print("Generating", path_file) 
        with open(path_file, "w") as path_f:
            path_f.write(f"""
NETCDF_INCDIR="-I{getenv("NETCDF_PATH")}/include"
NETCDF_LIBDIR="-L{getenv("NETCDF_PATH")}/lib"
NETCDF_LIB="-lnetcdf -lnetcdff"
HDF5_INCDIR="-I{getenv("HDF5_PATH")}/include"
HDF5_LIBDIR="-L{getenv("HDF5_PATH")}/lib"
HDF5_LIB="-lhdf5_hl -lhdf5 -lhdf5 -lz"
""")
        check_file_exists(fcm_file)
        check_file_exists(env_file)
        check_file_exists(path_file)