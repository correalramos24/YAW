
from pathlib import Path
from dataclasses import dataclass, field
from utils import *
from itertools import product

@dataclass
class AbstractRunner:
    """Contains the minimum parameters to run "something"
    """
    
    type : str = None
    rundir: Path = None
    log_name : str = None
    env_file: Path = None
    dry : bool = False
    cartesian : bool = False
    print_multi : bool = False

    required_fields = ["type", "rundir"]
    required_fields_msg = ", ".join(required_fields) + "are required arguments!"
    SINGLE_PARAMS   = [*required_fields, "dry", "ref_rundir", "rundir_files"]
    DELIM = "#"*33 + "-YAW-" + "#"*33

    help_dict = {
        "type" : "Type of runner",
        "rundir" : "Rundir path to execute the runner.",
        "log_name" : "Log file to dump the STDOUT and STDERR",
        "env_file" : "Environment file to use",
        "dry" : "Dry run, only generate running directory"
    }

    def __post_init__(self):
        """Finish the init of the class

        Raises:
            Exception: If some bad parameter found
        """
        # MANAGE PARAMETER TYPES:
        self.rundir = Path(self.rundir) if self.rundir else None
        if self.env_file:
            if is_a_list(self.env_file):
                self.env_file = [Path(f) for f in self.env_file]
            elif is_a_str(self.env_file):
                Path(self.env_file)
            else:
                raise Exception("Unrecognized type for env_file", 
                                type(self.env_file))
        
        # MULTI-PARAMTERS MANAGMENT:
        self.__init_multiparams()


        # EXPAND BASH ENV VARIABLES:
        self.__init_bash_env_variables()

    def __init_multiparams(self):
        """Initialize multiparams of the runner

        Raises:
            Exception: If the number of multi-parameters in no cartesian mode are different
        """
        params = self.__dict__
        uniparams   =   [
            k for k, v in params.items() 
            if not is_a_list(v) and not "__" in str(k)
        ]
        multiparams =   [
            k for k, v in params.items() 
            if is_a_list(v) and not "__" in str(k)
        ]
        if not multiparams: 
            return 
        # 1. Any multi-parameter ?:
        if (bad_multi_par := set(multiparams) & set(uniparams)):
            error("Forbbinde multi-params: ", ' '.join(bad_multi_par))
            raise Exception("Forbbinde multi-params: ", ' '.join(bad_multi_par))
        
        # 2. Way to join ?:
        if self.cartesian:
            # 2A. CARTESIAN
            info("Cartesian mode for multi-parameters", ' '.join(multiparams))
            multi_operation = product
        else:
            # 2B. ZIP MODE 
            info("Using zip mode (copy single parameters and" 
                "group by order multi-parameters)")

            # Check size len: all multi-params needs to be the same!
            b_lens = [
                len(params[multi_p]) == len(params[multiparams[0]]) 
                for multi_p in multiparams
            ]
            
            if not all(b_lens):
                critical("Invalid size for multi-parameters", 
                            [len(params[multi_p]) 
                            for multi_p in multiparams]
                        )
            
            # Set join operation
            multi_operation = zip
            
        # 3. Print if required:
        if self.print_multi:
            print("# Unique parameters:")
            print(
                '\n'.join(
                    f"> {k}: {v}" for k, v in self.__dict__.items() 
                    if v and not is_a_list(v) and 
                    not "__" in str(k) and not k == "print_multi"
                    and not k == "cartesian"
                )
            )
            print("# Combinations:")
            for i_comb, a in enumerate(multi_operation(
                                *[params[key_multi_par] 
                                for key_multi_par in multiparams])):
                comb_str = [f"{param}: {vale}" 
                            for param, vale in zip(multiparams, a)
                ]
                print(f"{i_comb} " + " | ".join(comb_str))

    def __init_bash_env_variables(self):
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        # Expand bash env variables
        for field, value in self.__dict__.items():
            if isinstance(value, str) and "$" in value:
                info("Expanding bash env var at", value)
                self.__dict__[field] = expand_env_variables(value)

    def manage_parameters(self):
        """Manage parameters to generate the environment for the run stage.
        """
        # Manage log file
        if self.log_name is None:
            print("WARNING: Not using a log, appending all to STDOUT")
        else:
            print(f"Using {self.log_name}, appending STDOUT and STDERR")
        # Manage rundir:
        if not check_path_exists(self.rundir):
            create_dir(self.rundir)
            print(f"Using {self.rundir} as rundir")
        else:
            print(f"WARNING, rundir {self.rundir} already exists!")
        
    def run(self):
        """Execute the runner
        """
        raise Exception("UNDEFINED RUN!")
    
    @classmethod
    def __generate_yaml_template_content(cls):
        ret = ""
        for parameter, comment in cls.help_dict.items():
            if parameter == "type":
                ret += f"  {parameter}: {cls.type}\n"
            else:
                ret += f"  {parameter}: #{comment}\n"
        return ret

    @classmethod
    def generate_yaml_template(cls):
        ret = f"{AbstractRunner.DELIM}\n## TEMPLATE FOR {cls.type} RUNNER\n"
        ret += "your_recipe_name:\n"
        ret += cls.__generate_yaml_template_content()
        ret += AbstractRunner.DELIM + '\n'

        with open(cls.type+".yaml", mode="w") as template:
            template.write(ret)

