# bot/utils/presets.py

LEADERBOARD_PRESETS = {
    "scores": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-highest_score": "true",
        "title": "Total plays",
        "description": "Counts distinct beatmaps played per user",
    },
    "plays": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-play": "true",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "title": "Total plays",
        "description": "Counts distinct beatmaps played per user, excluding D rank plays with difficulty removing mods",
    },
    "easyclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "title": "Total easy clears",
        "description": "Counts distinct beatmaps played per user, excluding difficulty removing mods (NF, RX)",
    },
    "normalclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "title": "Total (real) clears",
        "description": "Counts distinct beatmaps played per user, excluding difficulty removing (NF, RX) and difficulty reducing mods (HT, EZ)",
    },
    "hardclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-grade-not": "c,d",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-total_score-min": "400000",
        "title": "Total hard clears",
        "description": "Normal clear + standardized score must be at least 400,000 or higher. Play must be B rank or better",
    },
    "extraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-grade-not": "b,c,d",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-total_score-min": "650000",
        "title": "Total extra clears",
        "description": "Hard clear + score must be 650,000 or higher. Play must be an A rank or better",
    },
    "ultraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-grade-not": "b,c,d",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-total_score-min": "850000",
        "title": "Total ultra clears",
        "description": "Extra clear clear + standardized score must be 850000 or higher",
    },
    "overclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-accuracy-min": "0.99",
        "-is_fc": "true",
        "title": "Total overclears",
        "description": "Extra clear + must be FCed and accuracy must be 99 or higher",
    },
    "fc": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_fc": "true",
        "title": "Total (real) FCs",
        "description": "Counts distinct beatmaps per user where the score is a real full combo (is_fc=true) and disallows difficulty-removing and difficulty-reducing mods.",
    },
    "ss": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_ss": "true",
        "title": "Total (real) SSes",
        "description": "Counts distinct beatmaps per user where the score is a real SS (is_ss=true) and disallows difficulty-removing and difficulty-reducing mods.",
    },
    "s": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-grade-in": "s,sh",
        "title": "Total Ses",
        "description": "Counts distinct beatmaps per user where the grade is S or SH (grade-in=s,sh).",
    },
    "unique_fc": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_fc": "true",
        "-fc_count": "1",
        "title": "Unique FC count",
        "description": "Counts distinct beatmaps per user where they have the only valid FC on the map.",
    },
    "unique_ss": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_ss": "true",
        "-ss_count": "1",
        "title": "Unique SS count",
        "description": "Counts distinct beatmaps per user where they have the only valid SS on the map.",
    },
    "score": {
        "columns": "username, sum(total_score)",
        "-group": "username",
        "-order": "sum(total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Standardized)",
        "description": "Sums standardized score per user, restricted to the user's top leaderboard play (highest_score=true).",
    },
    "classicscore": {
        "columns": "username, sum(classic_total_score)",
        "-group": "username",
        "-order": "sum(classic_total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Classic Scaling)",
        "description": "Sums classic scaling score per user, restricted to the user's top leaderboard play (highest_score=true).",
    },
    "legacyscore": {
        "columns": "username, sum(legacy_total_score)",
        "-group": "username",
        "-order": "sum(legacy_total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Legacy)",
        "description": "Sums legacy score per user, restricted to the user's top leaderboard play (highest_score=true).",
    },
    "length": {
        "columns": "sum(length)",
        "alias": "length",
        "-group": "username",
        "-order": "sum(length)",
        "-highest_score": "true",
        "title": "Total length of scores",
        "description": "Sums length of scores matching the current filters.",
    },
    "sets": {
        "columns": "username, COUNT(DISTINCT beatmapset_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmapset_id)",
        "-grade-not": "d",
        "title": "Total plays",
        "description": "Counts plays on distinct beatmap sets (beatmapset_id) per user, excluding grade D results.",
    },
}

USER_PRESETS = {
    "playcount": {
        "columns": "username, total_play_count",
        "-order": "total_play_count",
        "title": "Total playcount",
        "description": "Ranks users by total_play_count",
    },
    "playtime": {
        "columns": "username, total_play_time",
        "-order": "total_play_time",
        "title": "Total playtime",
        "description": "Ranks users by total_play_time and displays time in hours",
    },
    "score": {
        "columns": "username, total_ranked_score",
        "-order": "total_ranked_score",
        "title": "Total ranked score",
        "description": "Ranks users by total_ranked_score",
    },
}

BEATMAP_PRESETS = {
    "length": {
        "columns": "sum(length)",
        "alias": "length",
        "title": "Total length of beatmaps",
        "description": "Sums beatmap length across a set of maps",
    },
    "count": {
        "columns": "count(*)",
        "alias": "count",
        "title": "Total beatmap count",
        "description": "Counts the number of beatmaps matching the current filters.",
    },
}

SCORE_PRESETS = {
    "length": {
        "columns": "sum(length)",
        "alias": "length",
        "title": "Total length of scores",
        "description": "Sums length of scores matching the current filters.",
    },
    "count": {
        "columns": "count(*)",
        "alias": "count",
        "title": "Total score count",
        "description": "Counts the number of scores matching the current filters.",
    },
    "score": {
        "columns": "sum(total_score)",
        "alias": "total_score",
        "title": "Score (standardized)",
        "description": "Sums standardized score (total_score) matching the current filters.",
    },
    "classicscore": {
        "columns": "sum(classic_total_score)",
        "alias": "classic_total_score",
        "title": "Score (classic)",
        "description": "Sums standardized score (classic_total_score) matching the current filters.",
    },
    "legacyscore": {
        "columns": "sum(legacy_total_score)",
        "alias": "legacy_total_score",
        "title": "Score (legacy)",
        "description": "Sums legacy score (legacy_total_score) matching the current filters.",
    }
}

LEADERBOARD_PRESET_SYNONYMS = {
    "plays": ("plays", "played", "play"),

    "scores": ("scores", "scored"),

    "easyclears": ("easyclears", "easyclear", "easycleared" "ec"),

    "normalclears": ("normalclears", "normalclear", "normalcleared", "nc", "clears", "clear", "cleared"),

    "hardclears": ("hardclears", "hardclear", "hardcleared", "hc"),

    "extraclears": ("extraclears", "extraclear", "extracleared", "exc"),

    "ultraclears": ("ultraclears", "ultraclear", "ultracleared", "uc"),

    "overclears": ("overclears", "overclear", "overcleared", "oc"),

    "fc": ("fc", "full_combo"),

    "ss": ("ss",),
    "s": ("s",),

    "unique_ss": ("unique_ss", "uss"),
    "unique_fc": ("unique_fc", "ufc"),

    "score": ("score", "standardized"),

    "classicscore": ("classicscore", "legacyscore"),

    "length": ("length",),

    "sets": ("sets", "beatmapsets"),
}

SCORE_PRESET_SYNONYMS = {
    "score": ("score", "standardized"),

    "classicscore": ("classicscore", "lazerscore"),

    "legacyscore": ("legacyscore", "stablescore"),


    "count": ("count",),
    "length": ("length",),
}


USER_PRESET_SYNONYMS = {
    "playcount": ("playcount",),
    "playtime": ("playtime",),
    "score": ("score",),
}

BEATMAP_PRESET_SYNONYMS = {
    "length": ("length", "playtime"),
    "count": ("count",),
}

LEADERBOARD_PRESET_LOOKUP = {
    alias.lower(): key
    for key, aliases in LEADERBOARD_PRESET_SYNONYMS.items()
    for alias in aliases
}

SCORE_PRESET_LOOKUP = {
    alias.lower(): key
    for key, aliases in SCORE_PRESET_SYNONYMS.items()
    for alias in aliases
}

BEATMAP_PRESET_LOOKUP = {
    alias.lower(): key
    for key, aliases in BEATMAP_PRESET_SYNONYMS.items()
    for alias in aliases
}

USER_PRESET_LOOKUP = {
    alias.lower(): key
    for key, aliases in USER_PRESET_SYNONYMS.items()
    for alias in aliases
}

def resolve_preset(name: str, presets: dict, synonyms: dict):
    if not name:
        return None

    canonical = synonyms.get(name.strip().lower())
    return presets.get(canonical)

def get_leaderboard_preset(name: str):
    return resolve_preset(name, LEADERBOARD_PRESETS, LEADERBOARD_PRESET_LOOKUP)

def get_user_preset(name: str):
    return resolve_preset(name, USER_PRESETS, USER_PRESET_LOOKUP)

def get_score_preset(name: str):
    return resolve_preset(name, SCORE_PRESETS, SCORE_PRESET_LOOKUP)

def get_beatmap_preset(name: str):
    return resolve_preset(name, BEATMAP_PRESETS, BEATMAP_PRESET_LOOKUP)

def resolve_any_preset(name: str):
    """
    Returns:
      (category, canonical_key, preset_dict, aliases_list)
    or None if not found.
    """

    name = name.lower()

    # Leaderboard presets
    canonical = LEADERBOARD_PRESET_LOOKUP.get(name)
    if canonical and canonical in LEADERBOARD_PRESETS:
        return (
            "leaderboard",
            canonical,
            LEADERBOARD_PRESETS[canonical],
            LEADERBOARD_PRESET_SYNONYMS.get(canonical, ())
        )

    # User presets
    canonical = USER_PRESET_LOOKUP.get(name)
    if canonical and canonical in USER_PRESETS:
        return (
            "user",
            canonical,
            USER_PRESETS[canonical],
            USER_PRESET_SYNONYMS.get(canonical, ())
        )

    # Beatmap presets
    canonical = BEATMAP_PRESET_LOOKUP.get(name)
    if canonical and canonical in BEATMAP_PRESETS:
        return (
            "beatmap",
            canonical,
            BEATMAP_PRESETS[canonical],
            BEATMAP_PRESET_SYNONYMS.get(canonical, ())
        )

    # Score presets
    canonical = SCORE_PRESET_LOOKUP.get(name)
    if canonical and canonical in SCORE_PRESETS:
        return (
            "score",
            canonical,
            SCORE_PRESETS[canonical],
            SCORE_PRESET_SYNONYMS.get(canonical, ())
        )

    return None