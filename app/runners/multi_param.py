from utils import *
from itertools import product

def is_a_multi_recipe(**params) -> bool:
    return  [
            param for param, val in params.items()
            if is_a_list(val) and not "__" in str(param)
        ]

def derive_multi_recipe(recipie_name, print_combs=False, **params) -> list[dict]:
    info("Deriving multiparameter for recipe", recipie_name)
    # 1. Get multiparameters:
    multiparams =   [
            param for param, val in params.items()
            if is_a_list(val) and not "__" in str(param)
        ]

    # 2. Generate variations according to the mode:
    if  "mode" in params.keys() and params["mode"]:
        # 2A. CARTESIAN
        join_op = product
        info("Cartesian mode for multi-parameters:", ' '.join(multiparams))
    else:
        # 2B. ZIP MODE 
        join_op = zip
        info("Using zip mode (copy single parameters and" 
            "group by order multi-parameters)")
        # Check params len: all multi-params needs to be the same!
        b_lens = [
            len(params[multi_p]) == len(params[multiparams[0]]) 
            for multi_p in multiparams
        ]
        
        if not all(b_lens):
            critical("Invalid size for multi-parameters", 
                        [len(params[multi_p]) for multi_p in multiparams])
            
    variations = list(join_op(
            *[params[key_multi_par] 
            for key_multi_par in multiparams])
    )
    print(f"Requested {len(variations)} executions with multiparams combinations")

    # 3. Print combinations:
    if print_combs:
        print("# Unique parameters:")
        print(
            '\n'.join(
                f"> {param}: {val}" for param, val in params.items() if
                    val and not is_a_list(val) and not "__" in str(param) and 
                    not param == "print_multi" and not param == "cartesian"
            )
        )
        print("# Combinations:")
        for i_comb, a in enumerate(variations):
            comb_str = [
                f"{param}: {vale}" 
                for param, vale in zip(multiparams, a)
            ]
            print(f"{i_comb} " + " | ".join(comb_str))

    # 4. Derive: Generate 1 recipe for each combination:
    # NOTE: The rundir needs to be modified accordingly!
    raise Exception("Multi-param executions not supported yet!")

    #self.root_rundir = self.rundir
    #self.rundir = []
    #for variation in self.variations:
    #    variation_folder = '_'.join(stringfy(value) for value in variation)
    #    self.rundir.append(Path(self.root_rundir, variation_folder))
    #print("# Rundirs:")
    #for r in self.rundir:
    #    print(">", r)
