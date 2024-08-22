
from abstract_runner import AbstractRunner
from slurm_runner import slurmRunner
from xios_compiler import xiosCompiler
from bash_runner import bashRunner
from pathlib import Path
import sys
import yaml

INPUT=sys.argv[1]

runners = {
    "slurm_runner": slurmRunner,
    "xios_compile": xiosCompiler,
    "bashRunner": bashRunner
}

def main():
    
    actions : list[AbstractRunner] = []
    print("Parsing", INPUT)
    with open(file=INPUT, mode='r') as yaml_file:
        content : dict = yaml.safe_load(yaml_file)
        for recipe_id, (name, content) in enumerate(content.items()):
            recipe_type = content["type"]
            if recipe_type in runners:
                print(f"Building recipe {recipe_id} ({recipe_type} - {name})")
                try:
                    r = runners[recipe_type](**content)
                    actions.append(r)
                except Exception as e:
                    print("EXCEPTION!", e)
                    print("Excluding recipe", recipe_id, name)
            else:
                print("Unrecognized recipe type", recipe_type)
    print("="*20)
    for i, action in enumerate(actions):
        print(f"Executing recipe {i}")
        action.manage_parameters()
        action.run()
        print("="*20)

if __name__ == "__main__":
    main()