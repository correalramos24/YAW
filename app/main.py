
from slurm_runner import slurmRunner

from pathlib import Path
import sys
import yaml

INPUT=sys.argv[1]

runners = {
    "slurm_runner": slurmRunner,
}

def main():
    
    actions = []

    with open(file=INPUT, mode='r') as yaml_file:
        content : dict = yaml.safe_load(yaml_file)
        for k, v in content.items():
            if k in runners:
                print(f"Building {k} recipe")
                a = runners[k](**v)
                actions.append(a)
                print(a)
            else:
                print("Unrecognized recipe", k)
            

    for action in actions:
        action.run()

if __name__ == "__main__":
    main()