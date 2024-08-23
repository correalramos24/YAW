from pathlib import Path
import argparse
from runners import *
from utils import *

# Declare the flags:
parser = argparse.ArgumentParser(description="YAW - Yet another workflow")
parser.add_argument('input', 
                    help="Select YAW recipe input file(S)", 
                    nargs ="*", type=Path)

parser.add_argument('--generate', help="Generate templeate to be \
                    filled by the user", choices=runners.keys())

# Parse the arguments:
app_args = parser.parse_args()

input_files : list[Path] =app_args.input
gen_template = app_args.generate

# Manage generation of templates:
if gen_template:
    info("Generting", gen_template, "template")

    runners[gen_template].generate_yaml_template()

    info("done")
    exit(0)
elif not input_files:
    error_and_exit("You must provide any YAW recipe!", 1)

