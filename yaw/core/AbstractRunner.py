
from utils import *
from pathlib import Path
from dataclasses import dataclass


@dataclass
class AbstractRunner:
    """Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None)
    """

    # BASIC PARAMETERS:
    type: str = None
    log_name: str = None
    env_file: Path = None
    dry: bool = False
    # INFO DERIVED FROM A MULTI-RECIPE:
    mode: str = None

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
        if self.log_name:
            info(f"Using {self.log_name}, appending STDOUT and STDERR")
        else:
            warning("Not using a log, appending all to STDOUT")

        if self.env_file:
            check_file_exists_exception(self.env_file)
        else:
            warning("Running without env!")

    def run(self):
        """Execute the runner
        """
        print("This is an empty runner!")

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
            ("dry", "Dry run, only manage parameters, not run anything"),
            ("comment", "BASIC PARAMETERS"), 
            ("log_name", "Log file to dump the STDOUT and STDERR"), 
            ("env_file", "Environment file to use"),
        ]
    
    # EXPAND BASH VARIABLES:
    def __init_bash_env_variables(self) -> None:
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        no_empty_params = {k : v for k, v in self.__dict__.items() if v}
        for param, value in no_empty_params.items():
            expanded_value = expand_bash_env_vars(value)
            if expanded_value:
                self.__dict__[param] = expanded_value

