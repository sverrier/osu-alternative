SCORE_LIVE_METADATA = {
    # Primary Key
    "id": {
        "type": "int",
        "nullable": False,
        "primary_key": True
    },
    
    # Score Metrics
    "accuracy": {
        "type": "float",
        "nullable": False,
        "range": (0, 100),
        "description": "Accuracy percentage"
    },
    "pp": {
        "type": "float",
        "nullable": True,
        "range": (0, None),
        "description": "Performance points"
    },
    "total_score": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Total score"
    },
    "classic_total_score": {
        "type": "int",
        "nullable": False,
        "range": (0, None),
        "description": "Classic scoring total"
    },
    "legacy_total_score": {
        "type": "int",
        "nullable": False,
        "range": (0, None),
        "description": "Legacy scoring total"
    },
    "total_score_without_mods": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Score without mod multipliers"
    },
    "combo": {
        "type": "int",
        "nullable": False,
        "range": (0, None),
        "description": "Maximum combo achieved"
    },
    
    # Grade and Status
    "grade": {
        "type": "str",
        "nullable": False,
        "enum": ["SS", "S", "A", "B", "C", "D", "SSH", "SH", "XH", "X", "F"],
        "description": "Score grade/rank"
    },
    "rank": {
        "type": "int",
        "nullable": True,
        "range": (1, None),
        "description": "Leaderboard rank"
    },
    
    # Boolean Flags
    "passed": {
        "type": "bool",
        "nullable": False,
        "description": "Whether the map was passed"
    },
    "is_perfect_combo": {
        "type": "bool",
        "nullable": False,
        "description": "Perfect combo (FC)"
    },
    "has_replay": {
        "type": "bool",
        "nullable": False,
        "description": "Replay available"
    },
    "replay": {
        "type": "bool",
        "nullable": False,
        "description": "Replay status"
    },
    "ranked": {
        "type": "bool",
        "nullable": False,
        "description": "Whether score is ranked"
    },
    "legacy_perfect": {
        "type": "bool",
        "nullable": False,
        "description": "Legacy perfect combo flag"
    },
    "preserve": {
        "type": "bool",
        "nullable": False,
        "description": "Preserve flag"
    },
    "processed": {
        "type": "bool",
        "nullable": False,
        "description": "Processing status"
    },
    "highest_score": {
        "type": "bool",
        "nullable": True,
        "description": "Highest score on this map"
    },
    "highest_pp": {
        "type": "bool",
        "nullable": True,
        "description": "Highest PP score on this map"
    },
    "difficulty_reducing": {
        "type": "bool",
        "nullable": True,
        "description": "Uses difficulty reducing mods"
    },
    "difficulty_removing": {
        "type": "bool",
        "nullable": True,
        "description": "Uses difficulty removing mods"
    },
    "is_fc": {
        "type": "bool",
        "nullable": True,
        "description": "Is an FC"
    },
    "is_ss": {
        "type": "bool",
        "nullable": True,
        "description": "Is an SS"
    },
    
    # Dates
    "ended_at": {
        "type": "datetime",
        "nullable": False,
        "description": "When the play ended"
    },
    "started_at": {
        "type": "datetime",
        "nullable": True,
        "description": "When the play started"
    },
    
    # IDs and References
    "best_id": {
        "type": "int",
        "nullable": True
    },
    "build_id": {
        "type": "int",
        "nullable": True
    },
    "legacy_score_id": {
        "type": "int",
        "nullable": True
    },
    "ruleset_id": {
        "type": "int",
        "nullable": False,
        "enum": [0, 1, 2, 3],
        "description": "Game mode: 0=osu, 1=taiko, 2=fruits, 3=mania"
    },
    
    # Statistics - Maximum
    "maximum_statistics_perfect": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_great": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_ignore_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_ignore_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_slider_tail_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_legacy_combo_increase": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_large_bonus": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_large_tick_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_small_bonus": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "maximum_statistics_small_tick_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    
    # Statistics - Actual
    "statistics_perfect": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Perfect/300 hits"
    },
    "statistics_great": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Great/100 hits"
    },
    "statistics_good": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Good/50 hits"
    },
    "statistics_ok": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "OK hits"
    },
    "statistics_meh": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Meh hits"
    },
    "statistics_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Miss count"
    },
    "statistics_ignore_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_ignore_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_slider_tail_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_slider_tail_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_large_bonus": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_large_tick_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_large_tick_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_small_bonus": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_small_tick_hit": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_small_tick_miss": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "statistics_combo_break": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    
    # Mods
    "mod_acronyms": {
        "type": "array",
        "nullable": True,
        "description": "Array of mod acronyms (HD, DT, etc.)"
    },
    "mod_speed_change": {
        "type": "float",
        "nullable": True,
        "range": (0.5, 2.0),
        "description": "Speed multiplier from mods"
    },
    
    # Type
    "type": {
        "type": "str",
        "nullable": False,
        "description": "Score type"
    },




    #GENERATED COLUMNS

}