import argparse
from pathlib import Path

from core.RunnerManager import RunnerManager
from yaw_ascii import *
from utils.utils_print2 import myLoggerLevels, myLogger
from utils.utils_bash import execute_command_get_ouput

# Version:
VERSION="v0.99.0 - Alfa"

def parse_log_level(level_str):
    try:
        return myLoggerLevels[level_str.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid log level: {level_str}")

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
    parser.add_argument("--parse", help="Only parse file(s)", 
                        action='store_true')
    
    parser.add_argument("--steps", metavar="S", nargs="*",
                        help="Run only step(s) with name R from the input recipies")

    parser.add_argument('--print-combinations', action='store_true',
                        help="Print combinations of multi-parameters")

    parser.add_argument('--version', help="Print YAW version", action='store_true')
    parser.add_argument('--dev-version', help="Print YAW version, detailed", action='store_true')

    parser.add_argument('--verbose', help="Set verbose level", 
                        type=parse_log_level, default=myLoggerLevels.INFO, 
                        choices=list(myLoggerLevels))    

    # Parse the arguments:
    if parser.parse_args().dev_version:
        yaw_home = Path(__file__).parent
        print("Yaw installed at", yaw_home)
        br = execute_command_get_ouput("git rev-parse --abbrev-ref HEAD", yaw_home)
        cm = execute_command_get_ouput("git rev-parse --short HEAD", yaw_home)
        tg = execute_command_get_ouput("git describe --tags --abbrev=0", yaw_home)
        print(f"VERSION: {VERSION} ({tg}) => BRANCH: {br} @ COMMIT: {cm}")
        print(logo_ascii)
        exit(0)
    if parser.parse_args().version:
        print(f"VERSION: {VERSION}")
        print(logo_ascii)
        exit(0)
        
    myLogger.set_verbose_lvl(parser.parse_args().verbose)

    return parser.parse_args()

