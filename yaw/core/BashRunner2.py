
from yaw.core.AbstractFileRunner2 import AbstractFileRunner2

from abc import abstractmethod
from dataclasses import dataclass, field, fields
from typing import Optional, Any

@dataclass(kw_only=True)
class BashRunner2(AbstractFileRunner2):
    bash_cmd    : str           = field(metadata={'kind': "R" , "desc": "Script to execute (./s.sh) or command (ls)"})
    args        : Optional[str] = field(default=None, metadata={'kind': "O" , "desc": "bash_cmd argument(s)"})
    wrapper     : Optional[str] = field(default=None, metadata={'kind': "O" , "desc": "wrapper bash_cmd"})
    script_name : Optional[str] = field(default="yaw_wrapper.sh", metadata={'kind': "O" , "desc": "script_name"})