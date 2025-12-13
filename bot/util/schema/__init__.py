from bot.util.schema.beatmapLive import BEATMAP_LIVE_METADATA
from bot.util.schema.scoreLive import SCORE_LIVE_METADATA
from bot.util.schema.userLive import USER_LIVE_METADATA

TABLE_METADATA = {
    "beatmapLive": BEATMAP_LIVE_METADATA,
    "scoreLive": SCORE_LIVE_METADATA,
    "userLive":  USER_LIVE_METADATA,
}

# Optional: normalize names so you can pass "beatmaplive", "BeatmapLive", etc.
_NORMALIZED_TABLE_NAMES = {
    name.lower(): name for name in TABLE_METADATA.keys()
}

def normalize_table_name(name: str) -> str:
    """
    Normalizes a table name to the canonical key used in TABLE_METADATA.
    Raises KeyError if not found.
    """
    if name in TABLE_METADATA:
        return name
    key = _NORMALIZED_TABLE_NAMES.get(name.lower())
    if key is None:
        raise KeyError(f"Unknown table: {name}")
    return key


def get_table_metadata(name: str) -> dict:
    """
    Returns the metadata dict for the given table name.
    """
    return TABLE_METADATA[normalize_table_name(name)]

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