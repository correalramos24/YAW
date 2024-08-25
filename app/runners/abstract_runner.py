
from pathlib import Path
from dataclasses import dataclass, field
from utils import *


@dataclass
class AbstractRunner:
    """Contains the minimum parameters to run "something". Builld 
    from a YAML recipe.
    It also defines required parameters as execution 
    parameters that cannot be null value (None)
    """
    
    # BASIC PARAMETERS:
    type : str = None                   
    rundir: Path | list[Path] = None                 
    log_name : str = None
    env_file: Path = None
    dry : bool = False
    # INFO DERIVED FROM A MULTI-RECIPE:
    mode : str = None
    root_recipe: str = None

    req_param = ["type", "rundir"]
    single_params   = [*req_param]
    DELIM = "#"*37 + "-YAW-" + "#"*38

    help_dict = {
        "type" : "Type of runner",
        "mode" : "cartesian | zip (default)",
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
        # Check required parameter:
        for param in self.req_param:
            if not self.__dict__[param]:
                error(param, "is a required argument!")

        # EXPAND BASH ENV VARIABLES:
        self.__init_bash_env_variables()

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

    def __init_bash_env_variables(self):
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        # Expand bash env variables
        for field, value in self.__dict__.items():
            if is_a_str(value) and "$" in value:
                log("Expanding bash env var at", value)
                self.__dict__[field] = expand_env_variables(value)
            if is_a_list(value) and "$" in ''.join(value):
                log("Searching bash env vars at", stringfy(value))
                for i, val in enumerate(value):
                    self.__dict__[field][i] = expand_env_variables(val)

    def manage_parameters(self):
        """Manage parameters to generate the environment for the run stage.
        """
        # Manage log file
        if self.log_name is None:
            info("WARNING: Not using a log, appending all to STDOUT")
        else:
            info(f"Using {self.log_name}, appending STDOUT and STDERR")
        # Manage rundir:
        
        if not check_path_exists(self.rundir):
            create_dir(self.rundir)
            info(f"Using {self.rundir} as rundir")
        else:
            info(f"rundir {self.rundir} already exists!")
        
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
        ret += "## Required parameters:" + ' '.join(cls.req_param) + "\n"
        ret += "## Single parameters: " + ' '.join(cls.single_params) + "\n"
        ret += "your_recipe_name:\n"
        ret += cls.__generate_yaml_template_content()
        ret += AbstractRunner.DELIM + '\n'

        with open(cls.type+".yaml", mode="w") as template:
            template.write(ret)

