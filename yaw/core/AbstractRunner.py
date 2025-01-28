
from utils import *
from pathlib import Path
from abc import ABC, abstractmethod

class AbstractRunner(ABC):
    """
    Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None)
    """
    YAML_DELIM = "#" * 37 + "-YAW-" + "#" * 38
    
    def __init__(self, **parameters):
        """
        Initialize runner. 
        Check the required arguments, expand bash variables and manage class types.
        Raises: 
            Exception: If some bad parameter found
        """
        self.parameters = parameters
        self.__check_req_parameters(parameters)
        self.__init_bash_env_variables()

        self.recipie_name = self._get_parameter_value("recipie_name")
        self.dry = self._get_parameter_value("dry", False)

        self.log_name = self._get_parameter_value("log_name")
        self.log_at_rundir = self._get_parameter_value("log_at_rundir")
        self.env_file = self._get_parameter_value("env_file")

        self.rundir = self._get_path_parameter("rundir")
        self.overwrite = self._get_parameter_value("overwrite", False)

        self.multi_params = self._get_parameter_value("multi_params", False)

    def get_name(self) -> str:
        return self.recipie_name

    def manage_parameters(self):
        """
        Generate the environment for the run stage.
        """
        info(f"Manage parameters for {self.recipie_name}...")
        if self.multi_params:
            self.manage_multi_recipie()
        # INIT RUNDIR
        if not self.rundir:
            self.rundir = Path(os.getcwd())
            info("Initializing rundir to the current path", self.rundir)
        else:
            if not check_path_exists(self.rundir):
                create_dir(self.rundir)
            elif check_path_exists(self.rundir) and not self.overwrite:
                raise Exception("Directory already exists, need overwrite: True")

        # INIT ENV
        if self.env_file:
            info("Using environment", self.env_file)
        else:
            warning("Environment not set!")

        # INIT LOG
        if self.log_name:
            info("Redirecting STDOUT and STDERR to", self.log_name, "log")
            if self.log_at_rundir:
                self.log_path = Path(self.rundir, self.log_name)
            else:
                self.log_path = Path(self.log_name)
        else: 
            self.log_path = None

    def manage_multi_recipie(self):
        aux = stringfy(self.multi_params)
        values = [stringfy(v) for k, v in self.__dict__.items() if k in self.multi_params]
        print("Tunning parameters from multirecipie!", aux)

        if self.rundir and not "rundir" in self.multi_params:
            info(f"Adding {aux} to rundir name ({values})")
            self.rundir = Path(self.rundir, '_'.join(values))
        if self.log_name and not self.log_at_rundir and not "log_name" in self.multi_params:
            info(f"Adding {aux} to log_name ({values})")
        if self.log_name:
            if '.' in self.log_name:
                last_point = self.log_name.rfind('.')
                self.log_name = self.log_name[:last_point] + '_'.join(values) + self.log_name[last_point:]
            else:
                self.log_name += '_'.join(values)

    @abstractmethod
    def run(self):
        pass

    def get_log_path(self):
        if not self.log_name:
            return None
        if self.log_at_rundir and self.log_name:
            return Path(self.rundir, self.log_name)
        else:
            return Path(self.log_name)

    #===============================PARAMETER METHODS===========================
    @classmethod
    def get_runner_type(cls) -> str:
        raise Exception("ABC!")

    @classmethod
    def get_parameters(cls) -> list[str]:
        return ["mode", "recipie_name", "type", "log_name",
                "log_at_rundir", "env_file", "rundir", 
                "mirror", "dry", "overwrite", "multi_params"
        ]

    @classmethod
    def get_required_params(cls) -> list[str]:
        """
        Return the required parameters
        """
        return ["type"]
    
    @classmethod
    def get_optional_params(cls) -> list[str]:
        return [param for param in cls.get_parameters() if 
                param not in cls.get_required_params()]

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        """
        Return the parameters that are multivalued
        """
        return set()

    @classmethod
    def __check_req_parameters(cls, params):
        req_params = cls.get_required_params()
        req_not_fill = \
            list(filter(lambda param : not params.get(param), req_params)
        )
        if len(req_not_fill) > 0:
            str_not_fill = stringfy(req_not_fill)
            raise Exception(f"Required argument(s) {str_not_fill} not found")

    #===========================EXPAND BASH VARIABLES===========================
    def __init_bash_env_variables(self) -> None:
        """Convert the bash variables ($VAR or ${VAR}) to the value.
        """
        no_empty_params = {k : v for k, v in self.parameters.items() 
                        if v and is_a_str(v) and "$" in v}
        for param, value in no_empty_params.items():
            expanded_value = expand_bash_env_vars(value)
            if expanded_value:
                self.parameters[param] = expanded_value
            else:
                raise Exception("Unable to find env variable for", value)

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def generate_yaml_template(cls) -> None:
        """
        Generate a YAML template for the runner
        """
        with open(cls.get_runner_type() + ".yaml", mode="w") as tmpl:
            tmpl.write(f"{cls.YAML_DELIM}\n## TEMPLATE FOR {cls.get_runner_type()} RUNNER\n")
            tmpl.write("## Required parameters:")
            tmpl.write(' '.join(cls.get_required_params()) + "\n")
            ##tmpl.write("## Optional parameters:")
            ##tmpl.write(' '.join(cls.get_optional_params()) + "\n")
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
                ret += f"  {parameter}: {cls.get_runner_type()}\n"
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

    #=============================PRIVATE METHODS===============================
    def _get_parameter_value(self, key: str, default_val: object = None) -> str:
        return self.parameters.get(key, default_val)


    def _get_path_parameter(self, key) -> Path:
        return safe_get_key(self.parameters, key, Path, None)


