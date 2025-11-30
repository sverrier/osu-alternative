"""
Database schema metadata for osu! tables.
Used for validation, query building, and help generation.
"""

BEATMAP_LIVE_METADATA = {
    # Primary Key
    "beatmap_id": {
        "type": "int",
        "nullable": False,
        "primary_key": True
    },
    "beatmapset_id": {
        "type": "int",
        "nullable": True
    },
    
    # Enumerated Fields
    "mode": {
        "type": "int",
        "nullable": True,
        "enum": [0, 1, 2, 3],
        "description": "Game mode: 0=osu, 1=taiko, 2=fruits, 3=mania"
    },
    "status": {
        "type": "str",
        "nullable": True,
        "enum": ["graveyard", "wip", "pending", "ranked", "approved", "qualified", "loved"],
        "description": "Beatmap status"
    },
    
    # Numeric Fields with Ranges
    "stars": {
        "type": "float",
        "nullable": True,
        "range": (0, 15),
        "description": "Star difficulty rating"
    },
    "od": {
        "type": "int",
        "nullable": True,
        "range": (0, 10),
        "description": "Overall Difficulty"
    },
    "ar": {
        "type": "float",
        "nullable": True,
        "range": (0, 10),
        "description": "Approach Rate"
    },
    "bpm": {
        "type": "float",
        "nullable": True,
        "range": (0, 1000),
        "description": "Beats per minute"
    },
    "cs": {
        "type": "float",
        "nullable": True,
        "range": (0, 10),
        "description": "Circle Size"
    },
    "hp": {
        "type": "float",
        "nullable": True,
        "range": (0, 10),
        "description": "HP Drain"
    },
    
    # Count/Duration Fields
    "length": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Total length in seconds"
    },
    "drain_time": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Drain time in seconds"
    },
    "count_circles": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "count_sliders": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "count_spinners": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "max_combo": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    
    # Statistics
    "pass_count": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "play_count": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    "fc_count": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "Full combo count"
    },
    "ss_count": {
        "type": "int",
        "nullable": True,
        "range": (0, None),
        "description": "SS rank count"
    },
    "favourite_count": {
        "type": "int",
        "nullable": True,
        "range": (0, None)
    },
    
    # Dates
    "ranked_date": {
        "type": "datetime",
        "nullable": True,
        "description": "Date when beatmap was ranked"
    },
    "submitted_date": {
        "type": "datetime",
        "nullable": True,
        "description": "Date when beatmap was submitted"
    },
    "last_updated": {
        "type": "datetime",
        "nullable": True,
        "description": "Last update timestamp"
    },
    
    # Text Fields
    "version": {
        "type": "str",
        "nullable": True,
        "description": "Difficulty name"
    },
    "title": {
        "type": "str",
        "nullable": True,
        "description": "Song title"
    },
    "artist": {
        "type": "str",
        "nullable": True,
        "description": "Song artist"
    },
    "source": {
        "type": "str",
        "nullable": True,
        "description": "Song source (anime, game, etc)"
    },
    "tags": {
        "type": "str",
        "nullable": True,
        "description": "Searchable tags"
    },
    "checksum": {
        "type": "str",
        "nullable": True,
        "description": "MD5 checksum"
    },
    "pack": {
        "type": "str",
        "nullable": True,
        "description": "Beatmap pack name"
    },
    
    # Special Fields
    "track_id": {
        "type": "int",
        "nullable": True,
        "description": "Featured artist track ID (NULL if not FA)"
    }
}

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
    "mods": {
        "type": "jsonb",
        "nullable": False,
        "description": "Mod configuration as JSON"
    },
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
    }
}

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

# Unified table access
TABLE_METADATA = {
    "beatmapLive": BEATMAP_LIVE_METADATA,
    "scoreLive": SCORE_LIVE_METADATA,
    "userLive": USER_LIVE_METADATA,
}

# Helper functions
def get_column_info(column, table=None):
    """
    Get metadata for a specific column.
    
    Args:
        column: Column name to look up
        table: Optional table name. If None, searches all tables.
    
    Returns:
        Dictionary with column metadata, or None if not found
    """
    if table:
        return TABLE_METADATA.get(table, {}).get(column)
    
    # Search all tables
    for table_meta in TABLE_METADATA.values():
        if column in table_meta:
            return table_meta[column]
    return None


def validate_column(column, table=None):
    """
    Check if column exists in schema.
    
    Args:
        column: Column name to validate
        table: Optional table name. If None, searches all tables.
    
    Returns:
        True if column exists, False otherwise
    """
    if table:
        return column in TABLE_METADATA.get(table, {})
    
    # Check all tables
    for table_meta in TABLE_METADATA.values():
        if column in table_meta:
            return True
    return False


def get_table_for_column(column):
    """
    Find which table contains a column.
    
    Args:
        column: Column name to search for
    
    Returns:
        Table name as string, or None if not found
    """
    for table_name, metadata in TABLE_METADATA.items():
        if column in metadata:
            return table_name
    return None


def get_all_columns(table=None):
    """
    Get list of all columns.
    
    Args:
        table: Optional table name. If None, returns all columns from all tables.
    
    Returns:
        List of column names
    """
    if table:
        return list(TABLE_METADATA.get(table, {}).keys())
    
    # Return all columns from all tables
    all_columns = set()
    for table_meta in TABLE_METADATA.values():
        all_columns.update(table_meta.keys())
    return list(all_columns)


def validate_value(column, value, operator="eq"):
    """
    Validate a value against column metadata.
    
    Args:
        column: Column name
        value: Value to validate
        operator: Operator being used (eq, min, max, etc.)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    meta = get_column_info(column)
    if not meta:
        return False, f"Unknown column: {column}"
    
    # Type validation
    col_type = meta.get("type")
    try:
        if col_type == "int":
            value = int(value)
        elif col_type == "float":
            value = float(value)
        elif col_type == "datetime":
            # Basic datetime format check (expand as needed)
            if not isinstance(value, str):
                return False, f"{column} requires a date string"
    except (ValueError, TypeError):
        return False, f"{column} expects type {col_type}, got {type(value).__name__}"
    
    # Range validation
    if "range" in meta and col_type in ("int", "float"):
        min_val, max_val = meta["range"]
        if min_val is not None and value < min_val:
            return False, f"{column} must be >= {min_val}"
        if max_val is not None and value > max_val:
            return False, f"{column} must be <= {max_val}"
    
    # Enum validation
    if "enum" in meta:
        if col_type == "str":
            value_check = value.lower()
            enum_check = [str(e).lower() for e in meta["enum"]]
        else:
            value_check = value
            enum_check = meta["enum"]
        
        if value_check not in enum_check:
            return False, f"{column} must be one of: {', '.join(map(str, meta['enum']))}"
    
    return True, None


def generate_help_text(column):
    """
    Generate help text for a column parameter.
    
    Args:
        column: Column name
    
    Returns:
        Help text string, or None if column not found
    """
    meta = get_column_info(column)
    if not meta:
        return None
    
    help_parts = [f"`-{column}`"]
    
    if "description" in meta:
        help_parts.append(f": {meta['description']}")
    
    details = []
    if "range" in meta:
        min_val, max_val = meta["range"]
        if min_val is not None and max_val is not None:
            details.append(f"Range: {min_val}-{max_val}")
        elif min_val is not None:
            details.append(f"Min: {min_val}")
        elif max_val is not None:
            details.append(f"Max: {max_val}")
    
    if "enum" in meta:
        details.append(f"Valid: {', '.join(map(str, meta['enum']))}")
    
    if details:
        help_parts.append(f" ({'; '.join(details)})")
    
    return "".join(help_parts)