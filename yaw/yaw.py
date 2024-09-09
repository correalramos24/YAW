from pathlib import Path
from arguments import parse_user_args
from core.RunnerManager import RunnerManager
from utils import *

def main():
    # 0. PARSE GENERIC ARGUMENTS:
    app_args = parse_user_args()
    input_files : list[Path] = app_args.input
    gen_template: str        = app_args.generate
    print_multi : bool       = app_args.print_combinations
    step_names  : list[str]  = app_args.steps
    # 0. PARSE ARGUMENTS THAT OVERRIDES RECIPIES:
    #TODO!

    manager = RunnerManager(input_files, step_names, print_multi)

    # 1. Manage generation of templates:
    if gen_template:
        info("Generating", gen_template, "template")
        manager.generate_template(gen_template)
        exit(0)

    if not input_files:
        critical("You must provide any YAW recipe!", "1")

    # 1. PARSE RECIPIE INPUT FILES:
    manager.parse_files()

    # 2. RUN RECIPE(S)
    manager.run_steps()


if __name__ == "__main__":

    main()