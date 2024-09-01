import argparse

from core.RunnerManager import RunnerManager
from utils import *

# Declare the flags:
parser = argparse.ArgumentParser(description="YAW - Yet another workflow")
parser.add_argument('input', 
                    help="Select YAW recipe input file(S)", 
                    nargs ="*", type=Path)

parser.add_argument('--generate', help="Generate template to be \
                    filled by the user", choices=RunnerManager.get_runners())

parser.add_argument("--steps", metavar="S", nargs="*",
                    help="Run only step(s) with name R from the input recipies")

parser.add_argument('--print-combinations', action='store_true',
                    help="Print combinations of multi-parameters")


# Parse the arguments:
app_args = parser.parse_args()

input_files : list[Path] = app_args.input
gen_template: str        = app_args.generate
print_multi : bool       = app_args.print_combinations
step_names  : list[str]  = app_args.steps

if step_names:
    info("Executing only", stringfy(step_names), "step(s)")

# Manage generation of templates:
if gen_template:
    info("Generating", gen_template, "template")
    RunnerManager.generate_template(gen_template)

    info("done")
    exit(0)

elif not input_files:
    critical("You must provide any YAW recipe!", "1")
