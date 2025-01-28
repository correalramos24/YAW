import argparse

from core.RunnerManager import RunnerManager
from yaw_ascii import *
from utils import *

# Version:
VERSION="v0.97.250"

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
    parser.add_argument('--dev-version', help="Print YAW version, detailed", action='store_true')

    parser.add_argument('--info', help="Add info messages", action='store_true')

    # Parse the arguments:
    if parser.parse_args().dev_version:
        br = execute_command_get_ouput("git rev-parse --abbrev-ref HEAD")
        cm = execute_command_get_ouput("git rev-parse --short HEAD")
        tg = execute_command_get_ouput("git describe --tags --abbrev=0")
        print(f"VERSION: {VERSION} ({tg}) => BRANCH: {br} @ COMMIT: {cm}")
        print(logo_ascii)
        exit(0)
    if parser.parse_args().version:
        print(f"VERSION: {VERSION}")
        print(logo_ascii)
        exit(0)

    return parser.parse_args()

