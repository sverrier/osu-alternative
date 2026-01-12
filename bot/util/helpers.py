from bot.util.schema import TABLE_METADATA

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

# Special cases that don't follow standard patterns
VALUED_PARAMS = {
    "-unplayed": (
        "NOT EXISTS (SELECT 1 FROM scoreLive s WHERE s.beatmap_id_fk = beatmapLive.beatmap_id AND s.ruleset_id = beatmapLive.mode AND s.user_id_fk = {value})",
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
    "-mods-exact": (
        "mod_acronyms @> {value} AND mod_acronyms <@ {value}",
        ["mod_acronyms"]
    ),
}

VALUELESS_PARAMS = {
    "-is_fa": ("track_id IS NOT NULL", ["track_id"]),
    "-not_fa": ("track_id IS NULL", ["track_id"]),
    "-has_replay": ("has_replay = true", ["has_replay"]),
    "-no_replay": ("has_replay = false", ["has_replay"]),
    "-convertless": ("scoreLive.ruleset_id = beatmapLive.mode", ["mode", "ruleset_id"]),
}

PARAM_SYNONYM_MAP = {
    "-u": "-username",
    "-drain": "-drain_time",
    "-y": "-year",
    "-c": "-country_code",
    "-a": "-artist-like",
    "-min": "-stars-min",
    "-max": "-stars-max",
    "-start": "-ranked_date-min",
    "-end": "-ranked_date-max",
    "-dir": "-direction",
    "-l": "-limit",
    "-p": "-page",
    "played-start": "-ended_at-min",
    "played-end": "-ended_at-max",
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


def escape_string(s):
    special_chars = {"'": "''", "\\": "\\\\", '"': ""}
    for char, escaped in special_chars.items():
        s = s.replace(char, escaped)
    return s

def get_args(arg=None):
    args = list(arg or [])
    di = {}

    i = 0
    while i < len(args):
        if args[i].startswith("-"):
            raw_key = args[i].lower()

            # Resolve synonyms immediately
            key = PARAM_SYNONYM_MAP.get(raw_key, raw_key)

            # Handle valueless params
            if key in VALUELESS_PARAMS:
                di[key] = True
                i += 1
                continue

            # Parameter expects a value
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                value = args[i + 1].lower()

                if " " in value:
                    raise ValueError(f"Spaces not allowed for argument {raw_key}")
                else:
                    di[key] = value

                i += 2
            else:
                raise ValueError(f"Parameter {raw_key} requires a value")
        else:
            i += 1

    # Clean numeric strings ("100_000" → "100000")
    for k, v in list(di.items()):
        if isinstance(v, str):
            if v.isdigit() or (v.replace("_", "").isdigit() and "." not in v):
                di[k] = v.replace("_", "")

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
        canonical = PARAM_SYNONYM_MAP.get(key, key)

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
        canonical = PARAM_SYNONYM_MAP.get(key, key)

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