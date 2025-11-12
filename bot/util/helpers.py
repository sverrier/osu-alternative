def escape_string(s):
    special_chars = {"'": "''", "\\": "\\\\", '"': ""}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def get_args(arg=None):
    args = list(arg or [])
    di = {}
    for i in range(0, len(args) - 1):
        if args[i].startswith("-"):
            key = args[i].lower()
            value = args[i + 1].lower()
            if key == "-u":
                di[key] = escape_string(value)
            elif " " in value:
                raise ValueError(f"Spaces not allowed for argument {key}")
            else:
                di[key] = value
    for k, v in di.items():
        if v.isdigit() or (v.replace("_", "").isdigit() and "." not in v):
            di[k] = v.replace("_", "")
    return di
