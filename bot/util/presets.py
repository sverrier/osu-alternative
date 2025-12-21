# bot/utils/presets.py

LEADERBOARD_PRESETS = {
    "scores": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "title": "Total plays",
        "description": "Counts distinct beatmaps per user (includes all grades). This is the raw 'played distinct maps' leaderboard with no clear/grade filtering.",
    },
    "plays": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-grade-not": "d",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "title": "Total plays",
        "description": "Counts distinct beatmaps per user, excluding grade D results (filters out failed/lowest-grade scores).",
    },
    "easyclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-grade-not": "d",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "title": "Total easy clears",
        "description": "Counts distinct cleared beatmaps per user (grade not D) while allowing difficulty-reducing mods but keeping difficulty-removing mods included (difficulty_removing=false).",
    },
    "normalclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-grade-not": "d",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "title": "Total (real) clears",
        "description": "Counts distinct cleared beatmaps per user (grade not D) and disallows both difficulty-removing and difficulty-reducing mods (difficulty_removing=false, difficulty_reducing=false).",
    },
    "hardclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-grade-notin": "c,d",
        "-total_score-min": "400000",
        "title": "Total extra clears",
        "description": "Counts distinct clears per user with stricter requirements: no difficulty-removing/reducing mods, grade must NOT be C or D, and total_score must be at least 400,000.",
    },
    "extraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-grade-notin": "b,c,d",
        "-total_score-min": "650000",
        "title": "Total extra clears",
        "description": "Counts distinct clears per user with high requirements: no difficulty-removing/reducing mods, grade must NOT be B/C/D (so A/S/SS-tier), and total_score must be at least 650,000.",
    },
    "ultraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-accuracy-min": "0.96",
        "-total_score-min": "850000",
        "title": "Total ultra clears",
        "description": "Counts distinct clears per user with very strict requirements: no difficulty-removing/reducing mods, accuracy must be at least 95%, and total_score must be at least 850,000.",
    },
    "overclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-grade-notin": "a,b,c,d",
        "-total_score-min": "1000000",
        "title": "Total overclears",
        "description": "Counts distinct clears per user at the top tier: no difficulty-removing/reducing mods, grade must NOT be A/B/C/D (i.e., S/SS-tier only), and total_score must be at least 1,000,000.",
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
    "a": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-grade": "a",
        "-highest_score": "true",
        "title": "Total As on leaderboard",
        "description": "Counts the number of beatmaps where a user's top score (highest_score=true) is grade A.",
    },
    "b": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-grade": "b",
        "-highest_score": "true",
        "title": "Total Bs on leaderboard",
        "description": "Counts the number of beatmaps where a user's top score (highest_score=true) is grade B.",
    },
    "c": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-grade": "c",
        "-highest_score": "true",
        "title": "Total Cs on leaderboard",
        "description": "Counts the number of beatmaps where a user's top score (highest_score=true) is grade C.",
    },
    "d": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-grade": "d",
        "-highest_score": "true",
        "title": "Total Ds on leaderboard",
        "description": "Counts the number of beatmaps where a user's top score (highest_score=true) is grade D.",
    },
    "unique_ss": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_ss": "true",
        "-ss_count": "1",
        "title": "Total (real) SSes",
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
        "description": "Ranks users by total_play_count (highest first).",
    },
    "playtime": {
        "columns": "username, total_play_time",
        "-order": "total_play_time",
        "title": "Total playtime",
        "description": "Ranks users by total_play_time (highest first) and displays time in hours",
    },
}

# bot/utils/presets.py
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

# bot/utils/presets.py
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
    "plays": "plays",
    "played": "plays",
    "play": "plays",

    "scores": "scores",
    "scored": "scores",

    "easyclears": "easyclears",
    "ec": "easyclears",

    "normalclears": "normalclears",
    "nc": "normalclears",
    "clears": "normalclears",
    "clear": "normalclears",

    "hardclears": "hardclears",
    "hc": "hardclears",

    "extraclears": "extraclears",
    "exc": "extraclears",

    "ultraclears": "ultraclears",
    "uc": "ultraclears",

    "overclears": "overclears",
    "oc": "overclears",

    "fc": "fc",
    "full_combo": "fc",

    "ss": "ss",
    "s": "s",
    "a": "a",
    "b": "b",
    "c": "c",
    "d": "d",

    "uss": "unique_ss",
    "unique_ss": "unique_ss",
    "ufc": "unique_fc",
    "unique_fc": "unique_fc",

    "score": "score",
    "standardized": "score",
    "classicscore": "classicscore",
    "legacyscore": "legacyscore",

    "sets": "sets",
    "beatmapsets": "sets",
}

SCORE_PRESET_SYNONYMS = {
    "plays": "plays",
    "played": "plays",
    "play": "plays",

    "scores": "scores",
    "scored": "scores",

    "easyclears": "easyclears",
    "ec": "easyclears",

    "normalclears": "normalclears",
    "nc": "normalclears",
    "clears": "normalclears",
    "clear": "normalclears",

    "hardclears": "hardclears",
    "hc": "hardclears",

    "extraclears": "extraclears",
    "exc": "extraclears",

    "ultraclears": "ultraclears",
    "uc": "ultraclears",

    "overclears": "overclears",
    "oc": "overclears",

    "fc": "fc",
    "full_combo": "fc",

    "ss": "ss",
    "s": "s",
    "a": "a",
    "b": "b",
    "c": "c",
    "d": "d",


    "uss": "unique_ss",
    "unique_ss": "unique_ss",
    "ufc": "unique_fc",
    "unique_fc": "unique_fc",

    "score": "score",
    "standardized": "score",
    "classicscore": "classicscore",
    "legacyscore": "legacyscore",

    "count":"count",
    "length":"length",
}


USER_PRESET_SYNONYMS = {
    "playcount": "playcount",
    "plays": "playcount",
    "total plays": "playcount",

    "playtime": "playtime",
    "time played": "playtime",
    "hours played": "playtime",
}

BEATMAP_PRESET_SYNONYMS = {
    "length": "length",
    "total length": "length",
    "playtime": "length",
}

def normalize_preset_key(value: str) -> str:
    return (
        value.lower()
             .replace("_", " ")
             .replace("-", " ")
             .strip()
    )

def resolve_preset(
    name: str,
    presets: dict,
    synonyms: dict,
):
    key = normalize_preset_key(name)
    canonical = synonyms.get(key)

    if not canonical:
        return None

    try:
        return presets[canonical]
    except KeyError:
        return None

def get_leaderboard_preset(name: str):
    return resolve_preset(name, LEADERBOARD_PRESETS, LEADERBOARD_PRESET_SYNONYMS)

def get_user_preset(name: str):
    return resolve_preset(name, USER_PRESETS, USER_PRESET_SYNONYMS)

def get_score_preset(name: str):
    return resolve_preset(name, SCORE_PRESETS, SCORE_PRESET_SYNONYMS)

def get_beatmap_preset(name: str):
    return resolve_preset(name, BEATMAP_PRESETS, BEATMAP_PRESET_SYNONYMS)

def invert_synonyms(syn_map: dict) -> dict:
    """canonical -> sorted list of aliases (excluding canonical itself)"""
    out = {}
    for alias, canonical in syn_map.items():
        out.setdefault(canonical, set()).add(alias)

    cleaned = {}
    for canonical, aliases in out.items():
        aliases = set(aliases)
        aliases.discard(canonical)
        cleaned[canonical] = sorted(aliases)
    return cleaned


_LEADERBOARD_ALIAS_MAP = invert_synonyms(LEADERBOARD_PRESET_SYNONYMS)
_USER_ALIAS_MAP = invert_synonyms(USER_PRESET_SYNONYMS)
_BEATMAP_ALIAS_MAP = invert_synonyms(BEATMAP_PRESET_SYNONYMS)


def resolve_any_preset(name: str):
    """
    Returns:
      (category, canonical_key, preset_dict, aliases_list)
    or None if not found.
    """
    key = normalize_preset_key(name)

    # Leaderboard presets
    canonical = LEADERBOARD_PRESET_SYNONYMS.get(key)
    if canonical and canonical in LEADERBOARD_PRESETS:
        return ("leaderboard", canonical, LEADERBOARD_PRESETS[canonical], _LEADERBOARD_ALIAS_MAP.get(canonical, []))

    # User presets
    canonical = USER_PRESET_SYNONYMS.get(key)
    if canonical and canonical in USER_PRESETS:
        return ("user", canonical, USER_PRESETS[canonical], _USER_ALIAS_MAP.get(canonical, []))

    # Beatmap presets
    canonical = BEATMAP_PRESET_SYNONYMS.get(key)
    if canonical and canonical in BEATMAP_PRESET_SYNONYMS:
        return ("beatmap", canonical, BEATMAP_PRESETS[canonical], _BEATMAP_ALIAS_MAP.get(canonical, []))

    return None
