from _ast import List

from app.utils import *
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class AbstractRunner:
    """Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None)
    """

    # BASIC PARAMETERS:
    type: str = None
    rundir: Path = None
    log_name: str = None
    env_file: Path = None
    dry: bool = False
    # INFO DERIVED FROM A MULTI-RECIPE:
    mode: str = None
    root_step: str = None

    req_param = ["type", "rundir"]
    multi_value_param = set()
    YAML_DELIM = "#" * 37 + "-YAW-" + "#" * 38

    def __post_init__(self):
        """Check the required arguments, expand bash variables
        and manage class types.

        Raises:
            Exception: If some bad parameter found
        """
        # CHECK REQ. ARGUMENTS:
        for param in self.req_param:
            if not self.__dict__[param]:
                raise Exception(f"{param} is a required argument!")

        # EXPAND BASH ENV VARIABLES:
        self.__init_bash_env_variables()

        # MANAGE PARAMETER TYPES:
        self.rundir = Path(self.rundir) if self.rundir else None
        self.env_file = Path(self.env_file) if self.env_file else None

        # MANAGE WARNINGS
        if not self.env_file:
            warning("Running without env!")

    def manage_parameters(self):
        """Generate the environment for the run stage.
        """
        # MANAGE RUNDIR:
        if not check_path_exists(self.rundir):
            create_dir(self.rundir)
            info(f"Using {self.rundir} as rundir")
        else:
            info(f"rundir {self.rundir} already exists!")
        # MANAGE LOG FILE
        if self.log_name is None:
            warning("Not using a log, appending all to STDOUT")
        else:
            info(f"Using {self.log_name}, appending STDOUT and STDERR")
        # MANAGE ENV:
        if self.env_file:
            check_file_exists_exception(self.env_file)

    def run(self):
        """Execute the runner
        """
        print("This is an empty runner!")

    @classmethod
    def get_parameters(cls) -> list[str]:
        return [str(p) for p in cls.__dict__.keys() if
                not p.startswith("_") and
                not p.isupper() and
                not callable(getattr(cls, p))
                ]


    def get_required_params(self) -> List(str):
        return self.req_param

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return cls.multi_value_param

    @classmethod
    def generate_yaml_template(cls):
        """
        Generate a YAML template for the runner
        """
        ret = f"{cls.YAML_DELIM}\n## TEMPLATE FOR {cls.type} RUNNER\n"
        ret += "## Required parameters:" + ' '.join(cls.req_param) + "\n"
        ret += "your_recipe_name:\n"
        ret += cls._generate_yaml_template_content()
        ret += cls.YAML_DELIM + '\n'

        with open(cls.type + ".yaml", mode="w") as template:
            template.write(ret)

    @classmethod
    def _generate_yaml_template_content(cls) -> str:
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
            ("comment", "SETUP"),
            ("type", "Type of runner"),
            ("mode", "cartesian | zip (default)"),
            ("dry", "Dry run, only generate running directory"),
            ("comment", "BASIC PARAMETERS"),
            ("rundir", "Rundir path to execute the runner."),
            ("log_name", "Log file to dump the STDOUT and STDERR"),
            ("env_file", "Environment file to use")
        ]

    def __init_bash_env_variables(self):
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        no_empty_params = {k : v for k, v in self.__dict__.items() if v}
        for param, value in no_empty_params.items():
            if is_a_str(value) and "$" in value:
                log("Expanding bash env var at", value)
                self.__dict__[param] = expand_env_variables(value)
            if is_a_list(value) and value[0] and "$" in ''.join(value):
                log("Searching bash env vars at", stringfy(value))
                for i, val in enumerate(value):
                    self.__dict__[param][i] = expand_env_variables(val)
