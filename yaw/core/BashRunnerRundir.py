from .BashRunner import BashRunner
from .RundirRunner import RundirRunner
from dataclasses import dataclass
from utils import *

@dataclass
class BashRunnerRundir(RundirRunner, BashRunner):
    type: str = "BashRunnerRundir"

    def run(self) -> bool:
        return super().run()