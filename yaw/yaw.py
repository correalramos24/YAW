from arguments import parse_user_args
from core.RunnerManager import RunnerManager
from utils import *
from utils.utils_print2 import *
from pathlib import Path

def main():
    # 0. PARSE APP ARGUMENTS:
    app_args = parse_user_args()
    input_files : list[Path] = app_args.input
    gen_template: str        = app_args.generate
    step_names  : list[str]  = app_args.steps
    parse       : bool       = app_args.parse

    if gen_template: # A. GENERATE TEMPLATE USE CASE:
        RunnerManager(None, None).generate_template(gen_template)
        myLogger.success("Generated", gen_template, "template")
        exit(0)
    else: # B. RUN RECIPIE USE CASE:
        if not input_files:
            myLogger.critical("You must provide any YAW recipe!", "1")
            exit(1)
            
        manager = RunnerManager(input_files, step_names)
        print("=" * 40 + "PARSING" + "=" * 40)
        manager.parse_files()
        manager.derive_recipies()
        print("=" * 87)
        if parse:
            print("PARSING ONLY ENABLED VIA --parse")
            print("FINISHING YAW...")
            return
        
        print("=" * 40 + "RUNNING" + "=" * 40)
        manager.run_steps()
        print("=" * 87)
        
        print("=" * 40 + "RESULTS" + "=" * 40)
        manager.print_results()
        print("=" * 87)

if __name__ == "__main__":
    main()