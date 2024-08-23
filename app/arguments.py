from pathlib import Path
import argparse
from runner_manager import runners

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
    print("Template generation for", gen_template)

    runners[gen_template].generate_yaml_template()

    print("done")
    exit(0)