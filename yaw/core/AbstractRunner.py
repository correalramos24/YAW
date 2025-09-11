
from utils.utils_controllers import metaAbstractClass
from utils.utils_files import *
from utils.utils_py import *
from utils.utils_bash import expand_bash_env_vars
from pathlib import Path
from abc import abstractmethod
from itertools import product
import os

class AbstractRunner(metaAbstractClass):
    """
    Contains the minimum parameters to run "something". Build
    from a YAML recipe. It also defines required parameters as execution
    parameters that cannot be null value (None).
    """
    
    def __init__(self, **parameters):
        """
        Initialize runner. 
        Check the required arguments, expand bash variables and manage class types.
        Raises: 
            Exception: If some bad parameter found
        """
        # Initialize parameters:
        self.parameters = parameters
        defaults = {k: v[0] for k, v in self.get_tmp_params().items()}
        merged_p = {**defaults, **parameters}
        [setattr(self, k, v) for k, v in merged_p.items()]

        # Parameter sanity checks & bash expansions:
        self.__check_req_parameters(parameters)
        self.__expand_bash_vars()   #TODO: Should I move this down?

        # Rundir or YAW invocation path:
        self.invoked_path = not self.rundir
        if self.create_dir and self.invoked_path:
            raise Exception("Create rundir is set but no rundir defined!")
            
        # Initialize runner results:
        self.set_result(0, "READY")
    
    @classmethod
    def get_tmp_params(cls) -> dict[str, (object|None, str, str)]:
        """
        Define the template params of the runner. Parameters are defined as:
        R: Required parameter - O: Optional parameter - S: Shadow parameter
        """
        return {
            "type": (None, "Type of runner", "R"),
            "mode": ("zip", "multi-parameter set: cartesian or zip (def)", "O"),
            "log_name": (None, "Log file to dump the STDOUT and STDERR.", "O"),
            "env_file": (None, "Environment file to use", "O"),
            "track_env" : ("env.log", "File name to store the env of a run", "O"),
            "rundir": (None, "Rundir path to execute the runner.", "O"),
            "create_dir": (True, "Create a rundir", "O"),
            "overwrite": (False, "Overwrite previous content of the rundir", "O"),
            "dry": (False, "Dry run, only manage parameters, not run anything", ""),
            "mirror": (None, "Execute several time the same step", "S"),
            "recipie_name": (None, "Name of the recipe", "S"),
        }

    def check_recipie(self):
        """
        Previous stage before manage_steps. Shows what is set in the recipie.
        Sets internal variables as well.
        """
        #TODO: Expand here bash and yaw variables!
        #ERROR if values not found
        if self.invoked_path:
            self.rundir = Path(os.getcwd())
            self._warn("Using curr. path as rundir!")
        if not self.create_dir:
            check_path_exists_exception(self.rundir)
        self._info("Runner rundir points @", self.rundir)
        
        if self.env_file:self._info(f"Using environment {self.env_file}")
        else: self._warn("Environment NOT set!")
        
        if self.log_name:
            self.log_path = Path(self.rundir, self.log_name)
            self._info("Redirecting output to", self.log_name)
        else: 
            self.log_path = None
            
    def manage_parameters(self):
        """
        Previous stage before run the runner. It manages the parameters
        and the environment.
        """
        self.__expand_yaw_vars()
        self.check_recipie()
        if self.create_dir: create_dir(self.rundir, self.overwrite)

    @abstractmethod
    def run(self): pass #ABC Method
    #======================RESULT METHODS=======================================
    def set_result(self, result: int, res_str: str):
        self.r_result, self.r_status = result, res_str

    def get_result(self) -> str:
        return f"{self.get_recipie_name()} #> {self.r_status} ({self.r_result})"
    #===============================PARAMETER METHODS===========================
    def get_recipie_name(self) -> str: return self.recipie_name
    
    @classmethod
    def get_parameters(cls) -> list[str]:
        return list(cls.get_tmp_params().keys())

    @classmethod
    def get_required_params(cls) -> list[str]:
        return [p for p, info in cls.get_tmp_params().items() if info[2] == "R"]
    
    @classmethod
    def get_optional_params(cls) -> list[str]:
        return [p for p, info in cls.get_tmp_params().items() if info[2] == "O"]

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
        multi_param_names = [param for param, _ in multi_params]
        self._info("Found multi-parameters for:", stringfy(multi_param_names))
        self._log(multi_params)
        unique_params = {
            param: value for param, value in self.parameters.items() 
            if param not in multi_param_names
        }
        
        # 2. CHECK MODE FOR VARIATION GENERATION:
        self._info(f"Deriving recipies using {self.mode}.")
        join_op = product if self.mode == "cartesian" else zip    
        
        # Check params len: all multi-params needs to be the same!
        if self.mode and not all([
            len(self.parameters[param]) == len(self.parameters[multi_params[0][0]])
            for param, _ in multi_params
        ]):
            Exception("Invalid size for multi-parameters",
                str([len(self.parameters[param]) for param, _ in multi_params]))
        
        # 3. GENERATE COMBINATIONS
        # TODO: Add support for mirror!
        variations_values = list(
            join_op(*[self.parameters[param] for param, _ in multi_params])
        )
        variations = [
            {**unique_params, **dict(zip(multi_param_names, variation))}
            for variation in variations_values
        ]
        self._log("# Found ", len(variations), "multi-params combs")
        for i_comb, variation in enumerate(variations):
            variation["recipie_name"] = f"{self.recipie_name}_{i_comb}"
            self._log(i_comb, variation)
            
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
            tmpl.write(f"{YAML_DELIM}\n## TEMPLATE FOR {cls.__name__}\n")
            #tmpl.write("## Required parameters:")
            #tmpl.write(' '.join(cls.get_required_params()) + "\n")
            #tmpl.write("## Optional parameters:")
            #tmpl.write(' '.join(cls.get_optional_params()) + "\n")
            tmpl.write(f"your_recipe_name:\n")
            tmpl.write(cls.__generate_yaml_template_content())
            tmpl.write(YAML_DELIM + "\n")

    @classmethod
    def __generate_yaml_template_content(cls) -> str:
        """
        Generate the content to be place in the template
        """
        ret = ""
        for parameter, comment in cls._inflate_yaml_template_info():
            if parameter == "type":
                ret += f"  {parameter}: {cls.__name__}\n"
            else:
                ret += f"  {parameter}: #{comment}\n"
        return ret

    @classmethod
    def _inflate_yaml_template_info(cls) -> list[(str, str)]:
        return [(param, info[1]) for param, info in 
            list(cls.get_tmp_params().items()) if info[2] != "S"]

    #===========================EXPAND BASH VARIABLES===========================
    def __expand_yaw_vars(self) -> None:
        yaw_vars_par = { 
            param: value for param, value in self.parameters.items()
            if is_a_str(value) and "&" in value
        }
        if len(yaw_vars_par) != 0:
            self._log("Expanding YAW for:", yaw_vars_par)
        
        for param, val_w_yaw_var in yaw_vars_par.items():
            expand_value = val_w_yaw_var 
            ii = search_char_in_str(expand_value, "&")
            while len(ii) >= 1:
                ref_param = expand_value[ii[0]+1:ii[1]]
                
                if not ref_param in self.parameters:
                    raise Exception(f"YAW var {ref_param} not found!")
                
                ref_value = self.parameters[ref_param]
                expand_value = expand_value[:ii[0]] + str(ref_value) + expand_value[ii[1]+1:]
                
                ii = search_char_in_str(expand_value, "&")
            
            if len(ii) == 1: 
                raise Exception(f"YAW variable error, you must close it with &")
            
            self._log(f"Expanding {param} from {val_w_yaw_var} to {expand_value}")
            self.parameters[param] = expand_value
        
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

