from .BashRunner import BashRunner
from .RundirHelper import RundirHelper
from dataclasses import dataclass
from pathlib import Path
from utils import *

@dataclass
class BashRunnerRundir(BashRunner, RundirHelper):
    type: str = "BashRunnerRundir"
    

    