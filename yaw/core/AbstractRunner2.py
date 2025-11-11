from utils import metaAbstractClass
import utils.utils_files as ufiles
from abc import abstractmethod
from dataclasses import dataclass, field, fields
from typing import Optional, Any

import os
from pathlib import Path

@dataclass(kw_only=True)
class AbstractRunner2(metaAbstractClass):

    type: str         = field(metadata={'kind': "R" , "desc": "Type of runner"})
    mode: str         = field(default="zip", metadata={"kind": "O",
                                                       "desc": "multi-parameter set: cartesian or zip (def)"})
    track_env: str    = field(default="env.log", metadata={"kind": "O",
                                                           "desc": "File name to store the env of a run"})
    create_dir: bool  = field(default=True, metadata={"kind": "O"})
    overwrite: bool   = field(default=False, metadata={"kind": "O"})
    dry: bool         = field(default=False, metadata={"kind": "O"})
    mirror: int       = field(default=None, metadata={"kind": "S"})
    recipie_name: str = field(default="recipie", metadata={"kind": "S"})
    log_name: Optional[str] = field(default=None, metadata={"kind": "O",
                                                            "desc": "Log file to dump STDOUT/STDERR"})
    env_file: Optional[str] = field(default=None, metadata={"kind": "O",
                                                            "desc": "Environment file to use"})
    rundir: Optional[Path | str] = field(default=None,metadata={"kind": "O",
                                                                "desc": "Rundir path to execute the runner"})

    invoked_path: bool = field(init=False)
    result: tuple[int, str] = field(init=False)
    log_file : Optional[Path] = field(init=False, default=None)

    def __post_init__(self):
        self.invoked_path = not self.rundir
        self.set_result(0, "READY")
        pass

    # ======================RUNNER INTERFACE====================================
    def check_parameters(self):
        self.__expand_bash_vars()

        if self.create_dir and self.invoked_path:
            raise Exception("Create rundir is set but no rundir defined!")
        if self.invoked_path:
            self.rundir = Path(os.getcwd())
            self._warn(f"Using current path as rundir! ({self.rundir})")
        if not self.create_dir: ufiles.check_path_exists_exception(self.rundir)
        if not self.env_file: self._warn("Environment NOT set!")
        if self.log_name:
            self.log_file = Path(self.rundir, self.log_name)
        self._ok("PARAMETERS CHECKED")
        self._ok("Rundir @", self.rundir)

    def manage_parameters(self):
        if self.create_dir: ufiles.create_dir(self.rundir, self.overwrite)
        self._ok("PARAMETERS MANAGED")

    @abstractmethod
    def run(self): pass

    def derive_recipie(self):
        pass

    #===============================PARAMETER METHODS===========================
    @classmethod
    def get_parameters(cls) -> list[str]: return [f.name for f in fields(cls)]

    @classmethod
    def get_required_params(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("kind") == "R"]

    @classmethod
    def get_optional_params(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.metadata.get("kind") == "O"]

    @classmethod
    def get_multi_value_params(cls) -> set[str]:
        return {f.name for f in fields(cls) if f.metadata.get("multi") is True}

    #======================RESULT METHODS=======================================
    def set_result(self, result: int, res_str: str): self.result = result, res_str

    def get_result(self) -> str:
        return f"{self.recipie_name} #> {self.result[0]} ({self.result[1]})"

    # =========================YAML GENERATION METHODS==========================
    @classmethod
    def generate_yaml_template(cls) -> None:
        """Generate a YAML template for the runner"""
        yaml_delim = "#" * 37 + "-YAW-" + "#" * 38
        with open(cls.__name__ + ".yaml", mode="w") as tmpl:
            tmpl.write(f"{yaml_delim}\n## TEMPLATE FOR {cls.__name__}\n")
            tmpl.write(f"your_recipe_name:\n")
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

    #=======================PRIVATE/INTERNAL METHODS=========================
    def _check_dry(self):
        """Generic dry method execution + set results"""
        self._ok("DRY MODE ENABLE!")
        self.set_result(0, "DRY RUN")
        return self.dry

    def __expand_yaw_vars(self):
        pass
    def __expand_bash_vars(self):
        pass

