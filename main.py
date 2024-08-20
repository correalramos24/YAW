
from pathlib import Path
import slurm_runner
import sys
import yaml

INPUT=sys.argv[1]

execution = {
    "slurm_runner": slurm_runner.slurm_runner,
}

def main():
    
    actions = []

    with open(file=INPUT, mode='r') as yaml_file:
        content : dict = yaml.safe_load(yaml_file)
        for k, v in content.items():
            if k in execution:
                print(f"Building {k} recipe")
                a = execution[k](**v)
                actions.append(a)
                print(a)
            else:
                print("Unrecognized recipe", k)
            



if __name__ == "__main__":
    main()