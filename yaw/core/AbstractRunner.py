
from utils.controllers import MetaAbstractClass
import utils.utils_files as ufiles
from utils.utils_py import is_str, search_char_in_str

from pathlib import Path
from abc import abstractmethod
from dataclasses import dataclass, field, fields
from typing import Optional, Any
import os


@dataclass(kw_only=True)
class AbstractRunner(MetaAbstractClass):
    """Contains the minimum parameters to run something """
    type: str = field(metadata={'kind': "R", "desc": "Type of runner"})
    mode: str = field(default="zip", metadata={"kind": "O", 
                      "desc": "multi-parameter set: cartesian or zip (def)"})
    track_env: str = field(default="env.log", metadata={"kind": "O", 
                           "desc": "File name to store the env of a run"})
    create_dir: bool = field(default=True, metadata={"kind": "O"})
    overwrite: bool = field(default=False, metadata={"kind": "O"})
    dry: bool = field(default=False, metadata={"kind": "O"})
    mirror: int = field(default=0, metadata={"kind": "O"})
    recipie_name: str = field(default="recipie", metadata={"kind": "S"})
    log_name: Optional[str] = field(default=None, metadata={"kind": "O", 
                                    "desc": "Log file to dump STDOUT/STDERR"})
    env_file: Optional[str] = field(default=None, metadata={"kind": "O", 
                                    "desc": "Environment file to use"})
    rundir: Optional[Path | str] = field(default=None, metadata={"kind": "O", 
                                         "desc": "Rundir path to execute the runner"})

    invoked_path: bool = field(default=None, metadata={"kind": "S"})
    result: tuple[int, str] = field(default=None, metadata={"kind": "S"})
    log_file: Optional[Path] = field(default=None, metadata={"kind": "S"})

    def __post_init__(self):
        self.invoked_path = not self.rundir
        self.set_result(0, "READY")

    def check_parameters(self):
        """Sanity checks for parameters after manage."""
        self.__expand_yaw_vars()
        self.__expand_bash_vars()

        if self.create_dir and self.invoked_path:
            raise Exception("Create rundir is set but no rundir defined!")
        if self.invoked_path:
            self.rundir = Path(os.getcwd())
            self._warn(f"Using current path as rundir! ({self.rundir})")
        if not self.create_dir: 
            ufiles.check_path_exists_exception(self.rundir)
        if not self.env_file: 
            self._warn("Environment NOT set!")
        if self.log_name:
            self.log_file = Path(self.rundir, self.log_name)

        self._info("Rundir @", self.rundir)

    def manage_parameters(self):
        """Previous stage before run the runner. It manages the parameters
        and the environment but didn't run anything.
        """
        if self.create_dir:
            ufiles.create_dir(self.rundir, self.overwrite)
        self._ok("PARAMETERS MANAGED")

    @abstractmethod
    def run(self): pass

    def check_dry(self) -> bool:
        """Generic dry method execution + set results"""
        self._ok("DRY MODE ENABLE!")
        self.set_result(0, "DRY RUN")
        return self.dry

    # ======================RESULT METHODS======================================
    def set_result(self, result: int, res_str: str): self.result = result, res_str

    def get_result(self) -> str:
        return f"{self.recipie_name} #> {self.result[0]} ({self.result[1]})"

    # ==============================PARAMETER METHODS===========================
    @classmethod
    def get_parameters(cls) -> list[str]:
        return [f.name for f in fields(cls)]

    def get_params_values(self) -> dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def get_required_params(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("kind") == "R"]

    @classmethod
    def get_optional_params(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("kind") == "O"]

    @classmethod
    def get_multivalue_params(cls) -> set[str]:
        return {f.name for f in fields(cls) if f.metadata.get("multi") is True}

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def generate_yaml_template(cls) -> None:
        """Generate a YAML template for the runner"""
        yaml_delim = "#" * 37 + "-YAW-" + "#" * 38
        with open(cls.__name__ + ".yaml", mode="w") as tmpl:
            tmpl.write(f"{yaml_delim}\n## TEMPLATE FOR {cls.__name__}\n")
            tmpl.write("recipe_name:\n")
            tmpl.write(cls.__generate_yaml_template_content())
            tmpl.write(yaml_delim + "\n")

    @classmethod
    def __generate_yaml_template_content(cls) -> str:
        """Generate the content to be place in the template"""
        ret = ""
        for parameter, comment in cls._inflate_yaml_template_info():
            if parameter == "type":
                ret += f"  {parameter}: {cls.__name__}\n"
            else:
                ret += f"  {parameter}: #{comment}\n"
        return ret

    @classmethod
    def _inflate_yaml_template_info(cls) -> list[tuple[str, str]]:
        return [(f.name, f.metadata.get("desc")) for f in fields(cls)
                if f.metadata.get("kind") != "S"]

    # ======================PRIVATE/INTERNAL METHODS============================
    def _check_dry(self):
        """Generic dry method execution + set results"""
        self._ok("DRY MODE ENABLE!")
        self.set_result(0, "DRY RUN")
        return self.dry

    def __expand_yaw_vars(self):
        yaw_vars_par = {p: v for p, v in self.get_params_values().items()
                        if is_str(v) and "&" in v}
        if len(yaw_vars_par) != 0: 
            self._log("Expanding YAW variables...")

        for param, val_w_yaw_var in yaw_vars_par.items():
            expand_value = val_w_yaw_var
            ii = search_char_in_str(expand_value, "&")
            while len(ii) >= 1:
                ref_param = expand_value[ii[0] + 1:ii[1]]

                if ref_param not in self.get_parameters():
                    raise Exception(f"YAW var {ref_param} not found!")

                ref_value = getattr(self, ref_param)
                expand_value = expand_value[:ii[0]] + str(ref_value) \
                + expand_value[ii[1] + 1:]

                ii = search_char_in_str(expand_value, "&")

            if len(ii) == 1:
                raise Exception("YAW variable error, you must close it with &")

            self._log(f"Expanding {param} from {val_w_yaw_var} to {expand_value}")
            setattr(self, param, expand_value)

    def __expand_bash_vars(self):
        """Convert the bash variables ($VAR or ${VAR}) to the value."""
        def expand_bash_env_vars(value: str | list[str]) -> str | list[str] | None:
            """Convert the bash variables ($VAR or ${VAR}) to the value."""
            if isinstance(value, str):
                return os.path.expandvars(value) if "$" in value else None
            if isinstance(value, list) and any("$" in v for v in value):
                return [os.path.expandvars(v) for v in value]
            return None
        bashed_pars = {p : v for p, v in self.get_params_values().items()
                       if v and is_str(v) and "$" in v}
        if len(bashed_pars) != 0: 
            self._log("Expanding bash variables...")
        for param, value in bashed_pars.items():
            expanded_value = expand_bash_env_vars(value)
            if expanded_value:
                setattr(self, param, expanded_value)
                self._log(f"Expanding {param} from {value} to {expanded_value}")
            else:
                raise Exception("Unable to find bash env variable for", value)
