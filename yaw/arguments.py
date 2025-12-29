from yaw.core.RunnerManager import RunnerManager
from yaw.yaw_ascii import logo_ascii

from utils.logger import LoggerLevels, MyLogger
from utils.git_project import GitProject

import argparse
from pathlib import Path

# Version:
VERSION = "v1.0"


def parse_log_level(level_str):
    try:
        return LoggerLevels[level_str.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid log level: {level_str}")


def parse_user_args():
    # Declare the flags:
    parser = argparse.ArgumentParser(description="YAW - Yet another workflow",
                                     usage="yaw.py input [input ...] [options]",
                                     epilog=f"VERSION: {VERSION}")
    parser.add_argument('input',
                        help="Select YAW recipe input file(S)",
                        nargs="*", type=Path)

    parser.add_argument('--generate', help="Generate template to be \
                        filled by the user", choices=RunnerManager.get_runners())
    parser.add_argument("--parse", help="Only parse file(s)",
                        action='store_true')

    parser.add_argument("--steps", metavar="S", nargs="*",
                        help="Run only step(s) with name R from the input recipies")

    parser.add_argument('--print-combinations', action='store_true',
                        help="Print combinations of multi-parameters")

    parser.add_argument('--version', help="Print YAW version", action='store_true')
    parser.add_argument('--dev-version', help="Print YAW version, detailed", 
                        action='store_true')

    parser.add_argument('--silent', help="Disable info printing", action='store_true')
    parser.add_argument('--info', help="Enable INFO printing", action="store_true")
    parser.add_argument('--log', help="Enable log printing", action="store_true")
    parser.add_argument('--debug', help="Enable log printing", action="store_true")

    # Parse the arguments:
    parsed = parser.parse_args()
    if parsed.version or parsed.dev_version:
        yaw_home = Path(__file__).parent
        print(f"VERSION: {VERSION}")
        print("Yaw installed at", yaw_home)
        if parsed.dev_version:
            print(GitProject(yaw_home))
        print(logo_ascii)
        exit(0)
    if parsed.log:
        MyLogger.set_verbose_level(LoggerLevels.LOG)
    if parsed.debug:
        MyLogger.set_verbose_level(LoggerLevels.DEBUG)
    if parsed.silent:
        MyLogger.set_verbose_level(LoggerLevels.NO)
    return parsed
