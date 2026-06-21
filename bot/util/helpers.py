from bot.util.schema import *

TABLE_COLUMNS = {
    "beatmapLive": list(TABLE_METADATA["beatmapLive"].keys()),
    "scoreLive": list(TABLE_METADATA["scoreLive"].keys()),
    "userLive": list(TABLE_METADATA["userLive"].keys())
}

JOIN_CLAUSES = {
    "scoreLive,beatmapLive": " inner join beatmapLive on scoreLive.beatmap_id_fk = beatmapLive.beatmap_id",
    "beatmapLive,scoreLive": " inner join scoreLive on beatmapLive.beatmap_id = scoreLive.beatmap_id_fk",
    "scoreLive,userLive": " inner join userLive on scoreLive.user_id_fk = userLive.user_id",
    "userLive,scoreLive": " inner join scoreLive on userLive.user_id = scoreLive.user_id_fk",
}

UTILITY_PARAMS = {"-name", "-field", "-precision", "-val-min", "-val-max"}

# Special cases that don't follow standard patterns
VALUED_PARAMS = {
    "-unplayed_by": (
        "NOT EXISTS (SELECT 1 FROM scoreLive s inner join userLive u on s.user_id_fk = u.user_id WHERE s.beatmap_id_fk = beatmapLive.beatmap_id AND s.ruleset_id = beatmapLive.mode AND UPPER(u.username) = UPPER('{value}'))",
        ["beatmap_id"]
    ),
    "-played_by": (
        "EXISTS (SELECT 1 FROM scoreLive s inner join userLive u on s.user_id_fk = u.user_id WHERE s.beatmap_id_fk = beatmapLive.beatmap_id AND s.ruleset_id = beatmapLive.mode AND UPPER(u.username) = UPPER('{value}'))",
        ["beatmap_id"]
    ),
    "-ssed_by": (
        "EXISTS (SELECT 1 FROM scoreLive s inner join userLive u on s.user_id_fk = u.user_id WHERE s.beatmap_id_fk = beatmapLive.beatmap_id AND s.ruleset_id = beatmapLive.mode AND UPPER(u.username) = UPPER('{value}') and is_ss = true)",
        ["beatmap_id"]
    ),
    "-fced_by": (
        "EXISTS (SELECT 1 FROM scoreLive s inner join userLive u on s.user_id_fk = u.user_id WHERE s.beatmap_id_fk = beatmapLive.beatmap_id AND s.ruleset_id = beatmapLive.mode AND UPPER(u.username) = UPPER('{value}') and is_fc = true)",
        ["beatmap_id"]
    ),
    "-search": (
        "LOWER(CONCAT(artist, ',', title, ',', source, ',', version, ',', tags)) LIKE LOWER({value})",
        ["artist", "title", "source", "version", "tags"]
    ),
    "-mods": (
        "mod_acronyms @> {value}",
        ["mod_acronyms"]
    ),
    "-mods-not": (
        "NOT (mod_acronyms @> {value})",
        ["mod_acronyms"]
    ),
    "-mods-exact": (
        "mod_acronyms @> {value} AND mod_acronyms <@ {value}",
        ["mod_acronyms"]
    ),
    "-packs": (
        "packs @> {value}",
        ["packs"]
    ),
}

VALUELESS_PARAMS = {
    "-is_fa": ("track_id IS NOT NULL", ["track_id"]),
    "-not_fa": ("track_id IS NULL", ["track_id"]),
    "-has_replay": ("has_replay = true", ["has_replay"]),
    "-no_replay": ("has_replay = false", ["has_replay"]),
    "-convertless": ("ruleset_id = mode", ["mode", "ruleset_id"]),
    "-not-overclear": ("(is_fc = false OR round(accuracy, 4) < 0.9900 OR difficulty_reducing = true OR difficulty_removing = true)", ["is_fc", "accuracy", "difficulty_reducing", "difficulty_removing"]),
    "-not-ultraclear": ("(total_score < 850000 OR grade IN ('B', 'C', 'D') OR difficulty_reducing = true OR difficulty_removing = true)", ["total_score", "accuracy"]),
    "-not-extraclear": ("(total_score < 650000 OR grade IN ('B', 'C', 'D') OR difficulty_reducing = true OR difficulty_removing = true)", ["total_score", "grade", "difficulty_reducing", "difficulty_removing"]),
    "-not-hardclear": ("(total_score < 400000 OR grade IN ('C', 'D') OR difficulty_reducing = true OR difficulty_removing = true)", ["total_score", "grade", "difficulty_reducing", "difficulty_removing"]),
    "-not-normalclear": ("(difficulty_reducing = true OR difficulty_removing = true)", ["difficulty_reducing", "difficulty_removing"]),
    "-not-easyclear": ("difficulty_removing = true", ["difficulty_removing"]),
    "-not-play": ("(difficulty_removing = true and grade = 'D')", ["difficulty_removing", "grade"]),
    "-play": ("(difficulty_removing = false OR grade != 'D')", ["difficulty_removing", "grade"]),
    "-is_lazer": ("build_id IS NOT NULL", ["build_id"]),
    "-is_stable": ("build_id IS NULL", ["build_id"]),
}

PARAM_ALIASES = {
    "-stars-min": ("-min",),
    "-stars-max": ("-max",),
    "-ranked_date-min": ("-start",),
    "-ranked_date-max": ("-end",),
    "-direction": ("-dir",),
    "-limit": ("-l",),
    "-page": ("-p",),
    "-ended_at-min": ("-played-start",),
    "-ended_at-max": ("-played-end",),
    "-not-overclear": ("-not-overcleared","-not-overclears",),
    "-not-ultraclear": ("-not-ultracleared","-not-ultraclears",),
    "-not-extraclear": ("-not-extracleared","-not-extraclears",),
    "-not-hardclear": ("-not-hardcleared","-not-hardclears",),
    "-not-normalclear": ("-not-normalcleared","-not-cleared","-not-clear""-not-clears","-not-normalclears",),
    "-not-easyclear": ("-not-easycleared","-not-easyclears",),
    "-not-play": ("-not-played","-not-plays",),
    "-play": ("-played","-plays",),
    "-unplayed_by": ("-unplayed",),
}

COLUMN_ALIASES = {
    "mod_speed_change": ("rate", "speed"),
    "grade": ("letter",), 
    "version": ("diff","diffname"), 
    "username": ("u","user"), 
    "drain_time": ("drain",), 
    "year": ("y",), 
    "country_code": ("c","country",), 
    "artist": ("a",), 
}

MODE_LABELS = {
    0: "osu",
    1: "taiko",
    2: "fruits",
    3: "mania",
    4: "total",
}

FA_LABELS = {
    0: "Non-FA",
    1: "FA",
    2: "All",
}

DIFF_LABELS = {
    0: "Easy",
    1: "Hard",
    2: "All",
}

SUFFIXES = (
    "-min",
    "-max",
    "-not",
    "-in",
    "-notin",
    "-like",
    "-regex",
)

COLUMN_ALIAS_LOOKUP = {}

for column, aliases in COLUMN_ALIASES.items():
    canonical = f"-{column}"

    for alias in aliases:
        COLUMN_ALIAS_LOOKUP[f"-{alias}"] = canonical

        for suffix in SUFFIXES:
            COLUMN_ALIAS_LOOKUP[f"-{alias}{suffix}"] = (
                f"{canonical}{suffix}"
            )

ALIAS_TO_PARAM = {
    alias: param
    for param, aliases in PARAM_ALIASES.items()
    for alias in aliases
}

ALIAS_TO_PARAM.update(COLUMN_ALIAS_LOOKUP)

def escape_string(s):
    special_chars = {"'": "''", "\\": "\\\\", '"': ""}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def is_param(token):
    token = token.lower()

    if not token.startswith("-"):
        return False

    if token in UTILITY_PARAMS:
        return True

    if token in VALUED_PARAMS:
        return True

    if token in VALUELESS_PARAMS:
        return True

    if token in PARAM_ALIASES:
        return True

    if token in ALIAS_TO_PARAM:
        return True

    raw = token.lstrip("-")

    for suffix in SUFFIXES:
        if raw.endswith(suffix):
            column = raw[:-len(suffix)]
            return validate_column(column)

    return validate_column(raw)

def get_args(arg=None):
    args = list(arg or [])
    di = {}

    i = 0
    while i < len(args):
        if is_param(args[i]):
            raw_key = args[i].lower()
            key = ALIAS_TO_PARAM.get(raw_key, raw_key)

            if key in VALUELESS_PARAMS:
                di[key] = True
                i += 1
                continue

            if i + 1 >= len(args):
                raise ValueError(f"Parameter {raw_key} requires a value")

            j = i + 1

            # Quoted value
            if args[j].startswith('"'):
                parts = [args[j]]

                while (
                    not parts[-1].endswith('"')
                    and j + 1 < len(args)
                ):
                    j += 1
                    parts.append(args[j])

                if not parts[-1].endswith('"'):
                    raise ValueError(
                        f"Unterminated quoted value for {raw_key}"
                    )

                value = " ".join(parts)[1:-1]

            # Unquoted value
            else:
                parts = []

                while j < len(args) and not is_param(args[j]):
                    parts.append(args[j])
                    j += 1

                if not parts:
                    raise ValueError(
                        f"Parameter {raw_key} requires a value"
                    )

                value = " ".join(parts)
                j -= 1

            di[key] = value.lower()
            i = j + 1

        else:
            i += 1

    return di

def separate_user_filters(di):
    """Separate user-only filters from all filters."""
    user_columns = set(TABLE_METADATA["userLive"].keys())
    user_args = {}

    suffixes = ["-min", "-max", "-not", "-in", "-notin", "-like", "-regex"]

    special_params = {
        "-order",
        "-direction"
    }

    for key, value in di.items():
        if not key.startswith("-"):
            continue

        # Resolve synonyms first, e.g. -y -> -year, -drain -> -drain_time, etc.
        canonical = ALIAS_TO_PARAM.get(key, key)

        # 1) Meta/special options that are always considered beatmap-side
        if canonical in special_params:
            user_args[key] = value
            continue

        # 1) Explicit VALUED_PARAMS definitions
        if canonical in VALUED_PARAMS:
            _, cols = VALUED_PARAMS[canonical]
            # Only treat as beatmap-only if *all* referenced columns are beatmap columns
            if all(col in user_columns for col in cols):
                user_args[key] = value
            continue

        # 2) Explicit VALUELESS_PARAMS definitions
        if canonical in VALUELESS_PARAMS:
            _, cols = VALUELESS_PARAMS[canonical]
            if all(col in user_columns for col in cols):
                user_args[key] = value
            continue

        # 3) Generic "-column[-suffix]" style parameters
        raw_key = canonical.lstrip("-")
        base_key = raw_key

        for suffix in suffixes:
            if raw_key.endswith(suffix):
                base_key = raw_key[:-len(suffix)]
                break

        if base_key in user_columns:
            user_args[key] = value

    return user_args

def separate_beatmap_filters(di):
    """Separate beatmap-only filters from all filters."""
    beatmap_columns = set(TABLE_METADATA["beatmapLive"].keys())
    beatmap_args = {}

    # Params that conceptually belong to beatmap queries but don't map
    # cleanly to a single column set (meta options)
    special_params = {
        "-field",
        "-precision",
        "-val-min",
        "-val-max",
    }

    suffixes = ["-min", "-max", "-not", "-in", "-notin", "-like", "-regex"]

    for key, value in di.items():
        if not key.startswith("-"):
            continue

        # Resolve synonyms first, e.g. -y -> -year, -drain -> -drain_time, etc.
        canonical = ALIAS_TO_PARAM.get(key, key)

        # 1) Meta/special options that are always considered beatmap-side
        if canonical in special_params:
            beatmap_args[key] = value
            continue

        # 2) Explicit VALUED_PARAMS definitions
        if canonical in VALUED_PARAMS:
            _, cols = VALUED_PARAMS[canonical]
            # Only treat as beatmap-only if *all* referenced columns are beatmap columns
            if all(col in beatmap_columns for col in cols):
                beatmap_args[key] = value
            continue

        # 3) Explicit VALUELESS_PARAMS definitions
        if canonical in VALUELESS_PARAMS:
            _, cols = VALUELESS_PARAMS[canonical]
            if all(col in beatmap_columns for col in cols):
                beatmap_args[key] = value
            continue

        # 4) Generic "-column[-suffix]" style parameters
        raw_key = canonical.lstrip("-")
        base_key = raw_key

        for suffix in suffixes:
            if raw_key.endswith(suffix):
                base_key = raw_key[:-len(suffix)]
                break

        if base_key in beatmap_columns:
            beatmap_args[key] = value

    return beatmap_args

def resolve_parameter(query: str):
    canonical = ALIAS_TO_PARAM.get(query, query)

    # Special valued
    if canonical in VALUED_PARAMS:
        return ("valued", canonical)

    # Valueless
    if canonical in VALUELESS_PARAMS:
        return ("valueless", canonical)

    # Column + suffix
    suffixes = ["-min", "-max", "-not", "-in", "-notin", "-like", "-regex"]

    for suffix in suffixes:
        if canonical.endswith(suffix):
            base = canonical[:-len(suffix)]
            if validate_column(base):
                return ("column_suffix", base, suffix)

    # Direct column param
    if canonical.startswith("-"):
        base = canonical[1:]
        if validate_column(base):
            return ("column", base)

    return None

PARAMETER_HELP = {
    "-page": {
        "description": "Page number for pagination",
        "usage": "`-page 2`",
    },
    "-limit": {
        "description": "Number of results per page",
        "usage": "`-limit 20`",
    },
    "-order": {
        "description": "Column to sort by",
        "usage": "`-order pp`",
    },
    "-direction": {
        "description": "Sort direction (ASC/DESC)",
        "usage": "`-direction DESC`",
    },
}