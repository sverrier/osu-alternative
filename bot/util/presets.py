# bot/utils/presets.py
SCORE_PRESETS = {
    "plays": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(*)",
        "title": "Total plays",
    },
    "easyclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-difficulty_removing": "false",
        "title": "Total easy clears",
    },
    "clears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "title": "Total normal clears",
    },
    "extraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-grade-notin": "c,d",
        "-total_score-min": "450000",
        "title": "Total extra clears",
    },
    "ultraclears": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-accuracy-min": "0.95",
        "-total_score-min": "750000",
        "title": "Total extra clears",
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
    },
    "fc": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_fc": "true",
        "title": "Total (real) FCs",
    },
    "ss": {
        "columns": "username, COUNT(DISTINCT beatmap_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmap_id)",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-is_ss": "true",
        "title": "Total (real) SSes",
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
    },
    "score": {
        "columns": "username, sum(total_score)",
        "-group": "username",
        "-order": "sum(total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Standardized)",
    },
    "classicscore": {
        "columns": "username, sum(classic_total_score)",
        "-group": "username",
        "-order": "sum(classic_total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Classic Scaling)",
    },
    "legacyscore": {
        "columns": "username, sum(legacy_total_score)",
        "-group": "username",
        "-order": "sum(legacy_total_score)",
        "-highest_score": "true",
        "title": "Ranked Score (Legacy)",
    },
    "sets": {
        "columns": "username, COUNT(DISTINCT beatmapset_id)",
        "-group": "username",
        "-order": "COUNT(DISTINCT beatmapset_id)",
        "-grade-not": "d",
        "title": "Total plays",
    },
}

USER_PRESETS = {
    "playcount": {
        "columns": "username, total_play_count",
        "-order": "total_play_count",
        "title": "Total playcount",
    },
    "playtime": {
        "columns": "username, total_play_time/3600",
        "-order": "total_play_time",
        "title": "Total playtime",
    },
}

# bot/utils/presets.py
BEATMAP_PRESETS = {
    "length": {
        "columns": "format_time_from_seconds(sum(length))",
        "title": "Total length of beatmaps",
    }
}