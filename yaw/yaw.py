
from arguments import *

def main():

    manager = RunnerManager(input_files, step_names, print_multi)

    # 1. PARSE RECIPIE INPUT FILES:
    manager.parse_files()

    # 2. RUN RECIPE(S)
    manager.run_steps()


if __name__ == "__main__":

    main()