# bot/utils/presets.py
PRESETS = {
    "plays": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-highest_score": "true",
        "-grade-not": "d",
        "title": "Total plays",
    },
    "clears": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-highest_score": "true",
        "-difficulty_removing": "false",
        "-grade-not": "d",
        "title": "Total clears",
    },
    "hardclears": {
        "columns": "username, COUNT(*)",
        "-group": "username",
        "-order": "COUNT(*)",
        "-highest_score": "true",
        "-difficulty_removing": "false",
        "-difficulty_reducing": "false",
        "-grade-not": "d",
        "title": "Total hard clears",
    },
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
