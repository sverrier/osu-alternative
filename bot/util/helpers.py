def escape_string(s):
    special_chars = {"'": "''", "\\": "\\\\", '"': ""}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def get_args(arg=None):
    args = list(arg or [])
    di = {}
    
    VALUELESS_PARAMS = {"-is_fa", "-not_fa", "-has_replay", "-no_replay"}
    
    i = 0
    while i < len(args):
        if args[i].startswith("-"):
            key = args[i].lower()
            
            # Fix valueless parameter
            if key in VALUELESS_PARAMS:
                di[key] = True 
                i += 1
                continue
            
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                value = args[i + 1].lower()
                if key == "-u":
                    di[key] = escape_string(value)
                elif " " in value:
                    raise ValueError(f"Spaces not allowed for argument {key}")
                else:
                    di[key] = value
                i += 2  # Skip both key and value
            else:
                raise ValueError(f"Parameter {key} requires a value")
        else:
            i += 1
    
    for k, v in di.items():
        if isinstance(v, str):
            if v.isdigit() or (v.replace("_", "").isdigit() and "." not in v):
                di[k] = v.replace("_", "")
    
    return di