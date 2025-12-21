USER_LIVE_METADATA = {
    # Primary Key
    "user_id": {
        "type": "int",
        "nullable": False,
        "primary_key": True
    },
    
    # User Info
    "username": {
        "type": "str",
        "nullable": False,
        "description": "Player username"
    },
    "country_code": {
        "type": "str",
        "nullable": True,
        "description": "2-letter country code"
    },
    "country_name": {
        "type": "str",
        "nullable": True,
        "description": "Full country name"
    },
    
    # Team Info
    "team_flag_url": {
        "type": "str",
        "nullable": True
    },
    "team_id": {
        "type": "int",
        "nullable": True
    },
    "team_name": {
        "type": "str",
        "nullable": True
    },
    "team_short_name": {
        "type": "str",
        "nullable": True
    },
}

# Generate mode-specific stats programmatically
_MODE_STATS_TEMPLATE = {
    "count_300": {"type": "int", "nullable": True, "range": (0, None)},
    "count_100": {"type": "int", "nullable": True, "range": (0, None)},
    "count_50": {"type": "int", "nullable": True, "range": (0, None)},
    "count_miss": {"type": "int", "nullable": True, "range": (0, None)},
    "global_rank": {"type": "int", "nullable": True, "range": (1, None)},
    "grade_counts_a": {"type": "int", "nullable": True, "range": (0, None)},
    "grade_counts_s": {"type": "int", "nullable": True, "range": (0, None)},
    "grade_counts_sh": {"type": "int", "nullable": True, "range": (0, None)},
    "grade_counts_ss": {"type": "int", "nullable": True, "range": (0, None)},
    "grade_counts_ssh": {"type": "int", "nullable": True, "range": (0, None)},
    "hit_accuracy": {"type": "float", "nullable": True, "range": (0, 100)},
    "level_current": {"type": "int", "nullable": True, "range": (0, None)},
    "level_progress": {"type": "int", "nullable": True, "range": (0, 100)},
    "maximum_combo": {"type": "int", "nullable": True, "range": (0, None)},
    "play_count": {"type": "int", "nullable": True, "range": (0, None)},
    "play_time": {"type": "int", "nullable": True, "range": (0, None), "description": "Play time in seconds"},
    "pp": {"type": "float", "nullable": True, "range": (0, None)},
    "ranked_score": {"type": "int", "nullable": True, "range": (0, None)},
    "replays_watched_by_others": {"type": "int", "nullable": True, "range": (0, None)},
    "total_hits": {"type": "int", "nullable": True, "range": (0, None)},
    "total_score": {"type": "int", "nullable": True, "range": (0, None)},
}

# Add mode-specific columns for osu, taiko, fruits, mania
for mode in ["osu", "taiko", "fruits", "mania"]:
    for stat, meta in _MODE_STATS_TEMPLATE.items():
        key = f"{mode}_{stat}"
        USER_LIVE_METADATA[key] = meta.copy()

# Add total (computed) columns
_TOTAL_STATS = {
    "total_grade_counts_a": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_grade_counts_s": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_grade_counts_sh": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_grade_counts_ss": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_grade_counts_ssh": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_play_count": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_play_time": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_pp": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_replays_watched_by_others": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
    "total_ranked_score": {"type": "int", "nullable": True, "range": (0, None), "computed": True},
}

USER_LIVE_METADATA.update(_TOTAL_STATS)

def _apply_display_hints(meta: dict[str, dict]) -> None:
    for key, m in meta.items():
        # don’t overwrite if you explicitly set one
        if "display" in m:
            continue

        # time in seconds -> hms
        if key.endswith("_play_time") or key == "total_play_time":
            m["display"] = "seconds_hms"
            continue

        # percent-ish fields (your metadata uses 0..100)
        if key.endswith("_hit_accuracy"):
            m["display"] = "percent_2"
            continue
        if key.endswith("_level_progress"):
            m["display"] = "percent_0"
            continue

        # pp (float)
        if key.endswith("_pp") or key == "total_pp":
            m["display"] = "pp_2"   # implement in formatting.py
            continue

        # combo
        if key.endswith("_maximum_combo"):
            m["display"] = "combo_x"  # implement in formatting.py
            continue

        # big ints: counts/scores/hits/grades/etc
        if (
            key.endswith("_ranked_score")
            or key.endswith("_total_score")
            or key.endswith("_total_hits")
            or key.endswith("_play_count")
            or key.startswith(("total_grade_counts_", "total_replays_", "total_ranked_"))
            or "_count_" in key                  # count_300/count_100/...
            or "grade_counts_" in key
            or "replays_watched_by_others" in key
        ):
            if m.get("type") == "int":
                m["display"] = "int_commas"

_apply_display_hints(USER_LIVE_METADATA)
