
from arguments import *
from runners import AbstractRunner, runners, derive_multi_recipe
from utils import *
import yaml
import traceback


def main():
    
    actions : list[AbstractRunner] = []
    # 1. PARSE
    for input in input_files:
        print("Parsing", input)

        with open(file=input, mode='r') as yaml_file:
            content : dict = yaml.safe_load(yaml_file)
            for recipe_id, (name, content) in enumerate(content.items()):
                print("-"*51)
                recipe_t = content["type"]
                info(f"Building recipe {recipe_id} ({recipe_t} - {name})")
                try:
                    if is_a_multi_recipe(**content):
                        sub_recipies = derive_multi_recipe(
                            name, print_multi, **content
                        )
                        for recipie in sub_recipies:
                            pass
                    else:
                        actions.append(runners[recipe_t](**content))
                except Exception as e:
                    error("While processing recipe ->", str(e))
                    log(traceback.format_exc())
                    print("Excluding recipe", recipe_id, "with name", name)
                    actions.append(None)
                
    print("="*20 + "END PARSING" + "="*20)

    # 2. RUN RECIPE(S)
    for i, action in enumerate(actions):
        print("-"*51)
        try:
            if action:
                print(f"Executing recipe {i}...")
                action.manage_parameters()
                action.run()
            else:
                print(f"Recipe {i} got an error during the parsing -> Skip")
        except Exception as e:
            warning(f"While executing recipe {i} ->", e)
            print(traceback.format_exc())
    print("="*20 + "END RUNNING" + "="*20)

if __name__ == "__main__":
    main()