from .BashRunner import BashRunner
from .RundirHelper import RundirHelper
from dataclasses import dataclass
from utils import *

@dataclass
class BashRunnerRundir(RundirHelper, BashRunner):
    type: str = "BashRunnerRundir"

    def run(self) -> bool:
        return super().run()