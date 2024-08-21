
from slurm_runner import slurmRunner
from xios_compiler import xiosCompiler
from abstract_runner import AbstractRunner
from pathlib import Path
import sys
import yaml

INPUT=sys.argv[1]

runners = {
    "slurm_runner": slurmRunner,
    "xios_compile": xiosCompiler
}

def main():
    
    actions : list[AbstractRunner] = []
    print("Parsing", INPUT)
    with open(file=INPUT, mode='r') as yaml_file:
        content : dict = yaml.safe_load(yaml_file)
        for recipe_id, (k, v) in enumerate(content.items()):
            if k in runners:
                print(f"Building recipe {recipe_id} ({k})")
                actions.append(runners[k](**v))
            else:
                print("Unrecognized recipe", k)
            
    for i, action in enumerate(actions):
        print(f"Executing recipe {i}")
        print(action)
        action.check_parameters()
        action.run()

if __name__ == "__main__":
    main()