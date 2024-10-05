from pathlib import Path

def safe_check_key_dict(d: dict, key: object) -> object:
    if key in d.keys():
        return d[key]
    else:
        return None
    
def safe_check_key_dict_int(d: dict, key: object, default_value: int) -> int:
    if key in d.keys():
        try:
            return int(d[key])
        except ValueError:
            return default_value
    else:
        return default_value


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

def listify(var: object) -> list:
    if is_a_list(var) or not var: 
        return var
    else:
        return [var]


def convert_path_to_str(p: Path) -> str:
    return str(p.name).replace("/", "-")

def convert_full_path_to_str(p: Path) -> str:
    return str(p).replace("/", "-")