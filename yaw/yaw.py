from arguments import parse_user_args
from core.RunnerManager import RunnerManager
from utils import *
from pathlib import Path

def main():
    # 0. PARSE GENERIC ARGUMENTS:
    app_args = parse_user_args()
    input_files : list[Path] = app_args.input
    gen_template: str        = app_args.generate
    print_multi : bool       = app_args.print_combinations
    step_names  : list[str]  = app_args.steps
    info_enable : bool       = app_args.info

    enable_info(info_enable)
    # 0. PARSE ARGUMENTS THAT OVERRIDES RECIPIES:

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

    # 2. DERIVE RECIPIES:
    manager.derive_recipies()

    # 3. RUN RECIPE(S)
    manager.run_steps()
    
    # 4. PRINT RESULTS:
    manager.print_results()


if __name__ == "__main__":

    main()