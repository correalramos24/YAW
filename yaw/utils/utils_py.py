from pathlib import Path

def safe_check_key_dict(d: dict, key: object) -> object:
    if key in d.keys():
        return d[key]
    else:
        return None


def is_a_list(var) -> bool:
    return isinstance(var, list)

def is_a_str(var) -> bool:
    return isinstance(var, str)

def is_a_path(var) -> bool:
    return isinstance(var, Path)

def stringfy(var) -> str:
    if is_a_path(var): 
        return convert_path_to_str(var)
    elif is_a_list(var):
        ret = str(var[0])
        for e in var[1:]:
            ret+= ',' +str(e)
        return ret
    else:
        return str(var)
    
def convert_path_to_str(p: Path) -> str:
    return str(p.name).replace("/", "-")

def convert_full_path_to_str(p: Path) -> str:
    return str(p).replace("/", "-")