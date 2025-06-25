
from utils import *
from pathlib import Path
from abc import ABC, abstractmethod
from itertools import product
from os.path import expandvars

class AbstractRunner(ABC):
    """
    Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None).
    
    Parameter description:
        - type: Type of the runner to be executed
        - mode: Mode to combine multi_parameters (zip or cartesian)
        - log_name: log name to redirect the output of the runner.
        - env_file: env_file to be used in the runner
        - rundir:   Select the rundir to execute the runner. 
                    If not set, the rundir will be set to the path from where YAW was invoked.
        - create_dir:   Create a new dir to execute the runner; if already exists it will raise an exception.
                        If false the runner will use the path from the rundir. It must be created before execute YAW.
        - overwrite: Overwrite the rundir, deleting all the content before executing the runner.
        - dry: Don't run anything, just setup the run.
        - mirror: Execute the same runner several times.
    """
    
    def __init__(self, **parameters):
        """
        Initialize runner. 
        Check the required arguments, expand bash variables and manage class types.
        Raises: 
            Exception: If some bad parameter found
        """
        self.parameters = parameters
        if self._gp("verbose"): enable_info(True)
        self.__check_req_parameters(parameters)
        self.__expand_bash_vars()
        
        # All the recipies run in the same dir?
        if self._gp("create_dir"):
            self.all_same_rundir = is_a_list(self._gp("rundir"))
        elif self._gp("rundir"):
            self.all_same_rundir = True
        else:
            self.all_same_rundir = False
                
        # Rundir or YAW current/invoked path:
        self.invoked_path = not self._gp("rundir")
        if self.invoked_path:
            self._sp("rundir", Path(os.getcwd()))
            self.runner_info("Init recipie rundir to the invoked path", self._gp("rundir"))
            
        # Initialize runner results:
        self.runner_result = 0
        self.runner_status = "READY"

    def recipie_name(self) -> str:
        """
        Get the name of the recipe. It is used to identify the recipe type
        """
        return self._gp("recipie_name")
    
    def is_runable(self) -> bool:
        return self.runner_status == "READY"
    
    @classmethod
    def get_params_dict(cls) -> dict[str, (object|None, str, str)]:
        """
        Define the parameters of the runner. The parameters are defined as a 
        dictionary with the parameter name as key and a tuple with the 
        default value, description and type of the parameter.
        The type of the parameter is defined as:
            - R: Required parameter
            - O: Optional parameter
            - S: Shadow parameter (for internal use)
        The default value is None if not defined.
        """
        return {
            "type": (None, "Type of runner", "R"),
            "mode": ("zip", "multi-parameter set: cartesian or zip (def)", "O"),
            "log_name": (None, "Log file to dump the STDOUT and STDERR.", "O"),
            "env_file": (None, "Environment file to use", "O"),
            "rundir": (None, "Rundir path to execute the runner.", "O"),
            "create_dir": (True, "Create a rundir", "O"),
            "overwrite": (False, "Overwrite previous content of the rundir", "O"),
            "dry": (False, "Dry run, only manage parameters, not run anything", "O"),
            "mirror": (None, "Execute several time the same step", "O"),
            "recipie_name": (None, "Name of the recipe", "S"),
            "verbose": (False, "Enable verbosity", "S"),
            "b_same_rundir": (False, "All recipies run in the same rundir", "S")
        }

    def manage_parameters(self):
        """
        Previous stage before run the runner. It manages the parameters
        and the environment.
        """
        # MANAGE MULTI RECIPE(s)
        self.manage_multi_recipie()
        
        # CREATE RUNDIR LOGIC
        if self.invoked_path:
            if not check_path_exists(self._gp("rundir")):
                self.runner_info("Creating rundir", self._gp("rundir"))
                create_dir(self._gp("rundir"))
        else:
            if self._gp("create_dir"):
                create_dir(self._gp("rundir"), self._gp("overwrite"))
            else:
                check_path_exists_exception(self._gp("rundir"))
                self.runner_info("Using rundir @", self._gp("rundir"))
        self.runner_info("Rundir set to", self._gp("rundir"))

        # INIT ENV
        if self._gp("env_file"):
            self.runner_info("Using environment", self._gp("env_file"))
        else:
            self.runner_info("Environment NOT set!")

        # INIT LOG
        if self._gp("log_name"):
            self.runner_info("Redirecting STDOUT and STDERR to", self._gp("log_name"), "log")
            if self._gp("log_at_rundir"):
                self.log_path = Path(self._gp("rundir"), self._gp("log_name"))
            else:
                self.log_path = Path(self._gp("log_name"))
        else: 
            self.log_path = None        

    @abstractmethod
    def manage_multi_recipie(self):
        """
        Step to manage the multi-recipie values.Executed before manage_parameters
        """
        pass #ABC Method

    @abstractmethod
    def run(self):
        pass
    
    def get_log_path(self):
        if not self._gp("log_name"):
            return None
        if self._gp("log_at_rundir") and self._gp("log_name"):
            return Path(self._gp("rundir"), self._gp("log_name"))
        else:
            return Path(self._gp("log_name"))
    #======================RESULT METHODS=======================================
    def set_result(self, result: bool, res_str: str):
        self.runner_result = result
        self.runner_status = res_str

    def get_result(self) -> str:
        return f"{self.recipie_name()} #> {self.runner_status} ({self.runner_result})"

    #===============================PARAMETER METHODS===========================
    @classmethod
    def get_parameters(cls) -> list[str]:
        return list(cls.get_params_dict().keys())

    @classmethod
    def get_required_params(cls) -> list[str]:
        return [p for p, info in cls.get_params_dict().items() if info[2] == "R"]
    
    @classmethod
    def get_optional_params(cls) -> list[str]:
        return [p for p, info in cls.get_params_dict().items() if info[2] == "O"]

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return set()

    @classmethod
    def __check_req_parameters(cls, params):
        # Check all required parameters are filled. If not, raise an exception:
        missing = [p for p in cls.get_required_params() if not params.get(p)]
        if missing:
            raise Exception(f"Not found req argument(s) {stringfy(missing)}")
        
        # Check if there are parameters not defined in the class:
        bad_params = [p for p in params.keys() if p not in cls.get_parameters()]
        if any(bad_params):
            raise Exception(f"Invalid parameter(s) {stringfy(bad_params)}")

    def derive_recipies(self) -> list["AbstractRunner"]:
        if not self.is_a_multirecipie(): return [self]

        # 1. SORT PARAMETERS:
        multi_params = [ (param, val) for param, val in self.parameters.items()
            if is_a_list(val) and
            not param in self.get_multi_value_params()
        ]
        print("Multi-parameters found:", multi_params)
        multi_param_names = [param for param, _ in multi_params]
        unique_params = {
            param: value for param, value in self.parameters.items() 
            if param not in multi_param_names
        }
        
        # 2. CHECK MODE FOR VARIATION GENERATION:
        if self._gp("mode") == "cartesian":
            join_op = product
            self.runner_print("Deriving recipies using cartesian product.")
        else: # ZIP MODE -> DEFAULT
            join_op = zip
            self.runner_print("Deriving recipies using zip mode.")
            # Check params len: all multi-params needs to be the same!
            b_length = [
                len(self.parameters[param]) == len(self.parameters[multi_params[0][0]])
                for param, _ in multi_params
            ]

            if not all(b_length):
                Exception("Invalid size for multi-parameters",
                    str([len(self.parameters[param]) for param, _ in multi_params]))
        
        # 3. GENERATE COMBINATIONS
        variations_values = list(
            join_op(*[self.parameters[param] for param, _ in multi_params])
        )
        variations = [
            {**unique_params, **dict(zip(multi_param_names, variation))}
            for variation in variations_values
        ]
        self.runner_info("# Found ", len(variations), "multi-params combinations")
        for i_comb, variation in enumerate(variations):
            variation["recipie_name"] = f"{self.recipie_name()}_{i_comb}"
            self.runner_info(i_comb, variation)
            
        # 4. RETURN DERIVED RECIPIES:
        return [self.__class__(**variation) for variation in variations]
    
    def is_a_multirecipie(self) -> bool:
        return any(
            is_a_list(val) and param not in self.get_multi_value_params()
            for param, val in self.parameters.items()
        )
    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def generate_yaml_template(cls) -> None:
        """
        Generate a YAML template for the runner
        """
        YAML_DELIM = "#" * 37 + "-YAW-" + "#" * 38
        with open(cls.__name__ + ".yaml", mode="w") as tmpl:
            tmpl.write(f"{YAML_DELIM}\n## TEMPLATE FOR {cls.__name__} RUNNER\n")
            tmpl.write("## Required parameters:")
            tmpl.write(' '.join(cls.get_required_params()) + "\n")
            tmpl.write("## Optional parameters:")
            tmpl.write(' '.join(cls.get_optional_params()) + "\n")
            tmpl.write(f"your_recipe_name:\n")
            tmpl.write(cls.__generate_yaml_template_content())
            tmpl.write(YAML_DELIM)

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
        return [(param, info[1]) for param, info in 
                list(cls.get_params_dict().items())]

    #=============================PRIVATE METHODS===============================
    def runner_print(self, *msg):
        print(f"{self.recipie_name()} #>", *msg)
    def runner_info(self, *msg):
        info(f"{self.recipie_name()} #>", *msg)
    
    def _gp(self, key: str) -> str:
        """
        Get parameter from the user. If the parameter is not found, it will
        return the default value defined in the class.
        """
        user_value = self.parameters.get(key, None)
        if user_value is None and key in self.get_params_dict():
            # Get pre-defined default value
            return self.get_params_dict()[key][0]
        else:
            return user_value

    def _sp(self, key: str, new_val: object) -> object:
        """
        Update the parameter with the new value. It returns the new value.
        """
        
        self.parameters[key] = new_val
        return self.parameters[key]


    def _get_path_parameter(self, key) -> Path:
        return safe_get_key(self.parameters, key, Path, None)

    #===========================EXPAND BASH VARIABLES===========================
    def __expand_bash_vars(self) -> None:
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

