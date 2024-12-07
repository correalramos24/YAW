
from utils import *
from pathlib import Path
from dataclasses import dataclass
from itertools import product


@dataclass
class AbstractRunner:
    """Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None)
    """

    # BASIC PARAMETERS:
    recipie_name : str
    type: str = None
    log_name: str = None
    log_at_rundir: bool = True
    env_file: Path = None
    rundir  : Path = None
    mirror : int = None
    dry: bool = False
    overwrite : bool =  False
    # INFO DERIVED FROM A MULTI-RECIPE:
    mode: str = None
    multi_params : list = None #Keep track of the multiparams of other runners
    YAML_DELIM = "#" * 37 + "-YAW-" + "#" * 38

    def __post_init__(self):
        """Check the required arguments, expand bash variables
        and manage class types.

        Raises:
            Exception: If some bad parameter found
        """
        self.__check_req_parameters()
        self.__init_bash_env_variables()

        self.env_file = Path(self.env_file) if self.env_file else None
        self.rundir = Path(self.rundir) if self.rundir else None

        if self.mirror: raise Exception("Yet to implement")

    def __check_req_parameters(self):
        req_params = self.get_required_params()
        req_not_fill = \
            list(filter(lambda param : not self.__dict__[param], req_params)
        )
        if len(req_not_fill) > 0:
            raise Exception("Required argument(s) "
                            f"{stringfy(req_not_fill)} not found")

    def manage_parameters(self):
        """Generate the environment for the run stage.
        """        
        if self.multi_params: 
            self.manage_multi_recipie()
        # INIT LOG
        if self.log_name:
            info(f"Redirecting STDOUT and STDERR to log {self.log_name}")
        # INIT ENV
        if self.env_file:
            check_file_exists_exception(self.env_file)
        else:
            warning("Running without env!")
        if self.overwrite:
            warning("OVERWRITE MODE ENABLED!")
        # INIT RUNDIR
        if not self.rundir:
            self.rundir = Path(os.getcwd())
            info("Initializing rundir to the current path", self.rundir)
        else:
            if not check_path_exists(self.rundir):
                create_dir(self.rundir)
            elif check_path_exists(self.rundir) and not self.overwrite:
                raise Exception("Directory already exists, need overwrite: True")


    def run(self) -> bool:
        """Execute the runner
        """
        raise Exception("Abstract runner called!")

    @property
    def log_path(self):
        if not self.log_name:
            return None
        if self.log_at_rundir and self.log_name:
            return Path(self.rundir, self.log_name)
        else:
            return Path(self.log_name)

    # PARAMETER METHODS:

    @classmethod
    def get_parameters(cls) -> list[str]:
        return [str(param) for param in cls.__dict__.keys() if
            not param.startswith("_") and not param.isupper() and
            not callable(getattr(cls, param))
        ]

    @classmethod
    def get_required_params(self) -> list[str]:
        return ["type"]

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return set()

    def manage_multi_recipie(self) -> None:
        aux = stringfy(self.multi_params)
        values = [stringfy(v) for k, v in self.__dict__.items() 
                                if k in self.multi_params]
        print("Tunning parameters from multirecipie!", aux)
        
        if self.rundir and not "rundir" in self.multi_params:
            info(f"Adding {aux} to rundir name")
            self.rundir = Path(self.rundir, '_'.join(values))
        if self.log_name and not self.log_at_rundir and not "log_name" in self.multi_params:
            info(f"Adding {aux} to log_name")
            if '.' in self.log_name:
                last_point = self.log_name.rfind('.')
                self.log_name = self.log_name[:last_point] + '_'.join(values) + self.log_name[last_point:]
            else:
                self.log_name += '_'.join(values)

    # YAML GENERATION METHODS:

    @classmethod
    def generate_yaml_template(cls) -> None:
        """
        Generate a YAML template for the runner
        """
        with open(cls.type + ".yaml", mode="w") as tmpl:
            tmpl.write(f"{cls.YAML_DELIM}\n## TEMPLATE FOR {cls.type} RUNNER\n")
            tmpl.write("## Required parameters:")
            tmpl.write(' '.join(cls.get_required_params()) + "\n")
            tmpl.write(f"your_recipe_name:\n")
            tmpl.write(cls.__generate_yaml_template_content())
            tmpl.write(cls.YAML_DELIM)

    @classmethod
    def __generate_yaml_template_content(cls) -> str:
        """
        Generate the content to be place in the template
        """
        ret = ""
        parameters_info = cls._inflate_yaml_template_info()
        for parameter, comment in parameters_info:
            if parameter == "type":
                ret += f"  {parameter}: {cls.type}\n"
            elif parameter == "comment":
                ret += f" # {comment}\n"
            else:
                ret += f"  {parameter}: #{comment}\n"

        return ret

    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        return [
            ("comment", "SETUP"), ("type", "Type of runner"),
            ("mode", "Type of multi-parameter: cartesian or zip (default)"),
            ("comment", "BASIC PARAMETERS"), 
            ("log_name", "Log file to dump the STDOUT and STDERR"), 
            ("log_at_rundir", "#Place the log file at the rundir.Default True"),
            ("env_file", "Environment file to use"),
            ("rundir", "Rundir path to execute the runner."),
            ("dry", "Dry run, only manage parameters, not run anything"),
            ("mirror", "Execute several time the same step"),
            ("overwrite", "Overwrite previous content of the rundir")
        ]
    
    # EXPAND BASH VARIABLES:
    def __init_bash_env_variables(self) -> None:
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        no_empty_params = {k : v for k, v in self.__dict__.items() 
                        if v and is_a_str(v) and "$" in v}
        for param, value in no_empty_params.items():
            expanded_value = expand_bash_env_vars(value)
            if expanded_value:
                self.__dict__[param] = expanded_value
            else:
                raise Exception("Unable to find env variable for", value)

