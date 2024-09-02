from .BashRunner import BashRunner
from .RundirRunner import RundirRunner
from dataclasses import dataclass
from pathlib import Path
from utils import *

@dataclass
class BashRunnerRundir(BashRunner, RundirRunner):
    type: str = "BashRunnerRundir"
    

    