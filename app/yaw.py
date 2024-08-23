
from arguments import *
from runner_manager import *
from abstract_runner import AbstractRunner

import yaml


def main():
    
    actions : list[AbstractRunner] = []
    # 1. PARSE
    for input in input_files:
        print("Parsing", input)

        with open(file=input, mode='r') as yaml_file:
            content : dict = yaml.safe_load(yaml_file)
            for recipe_id, (name, content) in enumerate(content.items()):
                recipe_t = content["type"]
                if recipe_t in runners:
                    print(f"Building recipe {recipe_id} ({recipe_t} - {name})")
                    try:
                        r = runners[recipe_t](**content)
                        actions.append(r)
                    except Exception as e:
                        print("EXCEPTION!", e)
                        print("Excluding recipe", recipe_id, name)
                else:
                    print("Unrecognized recipe type", recipe_t)
    
    print("="*20)

    # 2. RUN RECIPE(S)
    for i, action in enumerate(actions):
        print(f"Executing recipe {i}")
        action.manage_parameters()
        action.run()
        print("="*20)

if __name__ == "__main__":
    main()