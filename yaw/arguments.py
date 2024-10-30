import argparse

from core.RunnerManager import RunnerManager
from utils import *

# Version:
VERSION="v0.95"

def parse_user_args():
    # Declare the flags:
    parser = argparse.ArgumentParser(description="YAW - Yet another workflow",
                                    usage="yaw.py input [input ...] [options]", 
                                    epilog=f"VERSION: {VERSION}")
    parser.add_argument('input', 
                        help="Select YAW recipe input file(S)",
                        nargs ="*", type=Path)

    parser.add_argument('--generate', help="Generate template to be \
                        filled by the user", choices=RunnerManager.get_runners())

    parser.add_argument("--steps", metavar="S", nargs="*",
                        help="Run only step(s) with name R from the input recipies")

    parser.add_argument('--print-combinations', action='store_true',
                        help="Print combinations of multi-parameters")

    parser.add_argument('--version', help="Print YAW version", action='store_true')

    # Parse the arguments:

    if parser.parse_args().version:
        print(f"VERSION: {VERSION}")
        exit(0)

    return parser.parse_args()

