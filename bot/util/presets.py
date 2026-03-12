# bot/utils/presets.py

LEADERBOARD_PRESETS = {
    "scores": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "title": "Total plays",
        "description": "Counts distinct beatmaps played per user",
    },
    "plays": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-grade-not": "d",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "title": "Total plays",
        "description": "Counts distinct beatmaps played per user, excluding D rank plays",
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
    "count": "count",
    "total length": "length",
    "playtime": "length",
}

def resolve_preset(
    name: str,
    presets: dict,
    synonyms: dict,
):
    canonical = synonyms.get(name)

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

    # Leaderboard presets
    canonical = LEADERBOARD_PRESET_SYNONYMS.get(name)
    if canonical and canonical in LEADERBOARD_PRESETS:
        return ("leaderboard", canonical, LEADERBOARD_PRESETS[canonical], _LEADERBOARD_ALIAS_MAP.get(canonical, []))

    # User presets
    canonical = USER_PRESET_SYNONYMS.get(name)
    if canonical and canonical in USER_PRESETS:
        return ("user", canonical, USER_PRESETS[canonical], _USER_ALIAS_MAP.get(canonical, []))

    # Beatmap presets
    canonical = BEATMAP_PRESET_SYNONYMS.get(name)
    if canonical and canonical in BEATMAP_PRESET_SYNONYMS:
        return ("beatmap", canonical, BEATMAP_PRESETS[canonical], _BEATMAP_ALIAS_MAP.get(canonical, []))

    return None
