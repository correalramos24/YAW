
from arguments import *
from runners import AbstractRunner, runners
from utils import *
import yaml
import traceback


def main():
    
    actions : list[AbstractRunner] = []
    # 1. PARSE
    for input in input_files:
        info("Parsing", input)

        with open(file=input, mode='r') as yaml_file:
            content : dict = yaml.safe_load(yaml_file)
            for recipe_id, (name, content) in enumerate(content.items()):
                recipe_t = content["type"]
                if recipe_t in runners:
                    info(f"Building recipe {recipe_id} ({recipe_t} - {name})")
                    try:
                        r = runners[recipe_t](**content, print_multi = print_multi)
                        actions.append(r)
                    except Exception as e:
                        error("While processing recipe ->" + str(e))
                        #print(traceback.format_exc())
                        warning("Excluding recipe", recipe_id, name)
                else:
                    warning("Unrecognized recipe type", recipe_t)
    
    print("="*20)

    # 2. RUN RECIPE(S)
    for i, action in enumerate(actions):
        try:
            info(f"Executing recipe {i}")
            action.manage_parameters()
            action.run()
        except Exception as e:
            warning(f"While executing recipe {i} ->", e)
        print("="*20)

if __name__ == "__main__":
    main()