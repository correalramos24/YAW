from .arguments import parse_user_args
from yaw.core.RunnerManager import RunnerManager
from utils import *
from utils.utils_print import *
from pathlib import Path

def main():
    # 0. PARSE APP ARGUMENTS:
    app_args = parse_user_args()
    input_files : list[Path] = app_args.input
    gen_template: str        = app_args.generate
    step_names  : list[str]  = app_args.steps
    parse       : bool       = app_args.parse

    if gen_template: # A. GENERATE TEMPLATE USE CASE:
        RunnerManager([], []).generate_template(gen_template)
        MyLogger.success("Generated", gen_template, "template")
        exit(0)
    else: # B. RUN RECIPIE USE CASE:
        if not input_files:
            MyLogger.critical("You must provide any YAW recipe!", "1")
            exit(1)

        manager = RunnerManager(input_files, step_names)
        print("=" * 40 + "PARSING" + "=" * 40)
        manager.parse_files()
        print("=" * 40 + "DERIVING" + "=" * 39)
        manager.derive_recipies()
        if parse:
            print("PARSING ONLY ENABLED VIA --parse")
            print("FINISHING YAW...")
            return

        print("=" * 40 + "RUNNING" + "=" * 40)
        manager.run_steps()

        print("=" * 40 + "RESULTS" + "=" * 40)
        manager.print_results()

if __name__ == "__main__":
    main()
