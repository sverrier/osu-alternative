from __future__ import annotations

from typing import Any, Callable

from bot.util.schema import TABLE_METADATA

Formatter = Callable[[Any], str]

def fmt_int_commas(v: Any) -> str:
    """Format integer with thousands separators."""
    return "-" if v is None else f"{int(v):,}"


def fmt_seconds_hms(v: Any) -> str:
    """Format seconds as human-readable HhMmSs, omitting leading zero units."""
    if v is None:
        return "-"

    s = int(v)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)

    parts = []

    if h > 0:
        parts.append(f"{h}h")
        parts.append(f"{m:02d}m")
        parts.append(f"{s:02d}s")
    elif m > 0:
        parts.append(f"{m}m")
        parts.append(f"{s:02d}s")
    else:
        parts.append(f"{s}s")

    return "".join(parts)


def fmt_float(decimals: int) -> Formatter:
    """Factory for fixed-decimal float formatters."""
    def _f(v: Any) -> str:
        return "-" if v is None else f"{float(v):.{decimals}f}"
    return _f

def fmt_percent_0(v: Any) -> str:
    return "-" if v is None else f"{float(v):.0f}%"


def fmt_percent_2(v: Any) -> str:
    return "-" if v is None else f"{float(v):.2f}%"


def fmt_pp_2(v: Any) -> str:
    return "-" if v is None else f"{float(v):.2f}pp"


def fmt_combo_x(v: Any) -> str:
    return "-" if v is None else f"{int(v)}x"


FORMATTERS: dict[str, Formatter] = {
    "int_commas": fmt_int_commas,
    "seconds_hms": fmt_seconds_hms,
    "float_2": fmt_float(2),
    "percent_0": fmt_percent_0,
    "percent_2": fmt_percent_2,
    "pp_2": fmt_pp_2,
    "combo_x": fmt_combo_x,
}


# Field (output-alias) specific overrides.
# These take precedence over schema metadata.
FIELD_FORMAT: dict[str, Formatter] = {
    "play_count": lambda v: f"{fmt_int_commas(v)} plays",
    "pass_count": lambda v: f"{fmt_int_commas(v)} passes",
    "favourite_count": lambda v: f"{fmt_int_commas(v)} favs",
    "max_combo": lambda v: "-" if v is None else f"{int(v)}x",
    "length": fmt_seconds_hms,
    "count": fmt_int_commas,
    "sum": fmt_int_commas,
    "percent": fmt_percent_2,
    "drain_time": fmt_seconds_hms,
    "playtime": fmt_seconds_hms,
    "total_score": fmt_int_commas,
    "classic_total_score": fmt_int_commas,
    "legacy_total_score": fmt_int_commas,
}


def format_field(
    field_name: str,
    value: Any,
    table: str | None = None,
    *,
    alias: str | None = None,
) -> str:
    """
    Central formatting resolver.

    Prefer calling this at the final display boundary (embed/table/csv rendering).

    Rules (in order):
      1) FIELD_FORMAT override by output key (alias first, then field_name)
      2) Schema metadata display hint (table-scoped if provided, else search known tables)
      3) Generic fallback for ints -> commas
      4) Default str() (or "-" for None)
    """
    key = alias or field_name

    # 1) field override (by output key)
    if key in FIELD_FORMAT:
        return FIELD_FORMAT[key](value)

    # 2) schema hint (if known)
    if table:
        meta = TABLE_METADATA.get(table, {})
        if key in meta:
            disp = meta[key].get("display")
            if disp in FORMATTERS:
                return FORMATTERS[disp](value)
    else:
        # try to find a matching column in any known table metadata
        for _t, meta in TABLE_METADATA.items():
            if key in meta:
                disp = meta[key].get("display")
                if disp in FORMATTERS:
                    return FORMATTERS[disp](value)
                break

    # 3) generic fallback
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return fmt_int_commas(value)

    # 4) default
    return "-" if value is None else str(value)