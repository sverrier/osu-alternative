import json
from .jsonDataObject import jsonDataObject

class ScoreMania(jsonDataObject):
    table = "scoreMania"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"mods", "current_user_attributes"}  # JSONB fields
    date_columns = {"ended_at", "started_at"} 
    flatten_columns = {"statistics", "maximum_statistics"}  # Flattened fields
    column_list =  ["accuracy", "beatmap_id", "best_id", "build_id", "classic_total_score", "current_user_attributes", "ended_at", "has_replay", "id", "is_perfect_combo", "legacy_perfect", "legacy_score_id", "legacy_total_score", "max_combo", "maximum_statistics_legacy_combo_increase", "maximum_statistics_perfect", "maximum_statistics_ignore_hit", "mods", "passed", "pp", "preserve", "processed", "rank", "ranked", "replay", "ruleset_id", "started_at", "statistics_combo_break", "statistics_perfect", "statistics_great", "statistics_good", "statistics_ok", "statistics_meh", "statistics_miss", "statistics_ignore_hit", "statistics_ignore_miss", "total_score", "total_score_without_mods", "type", "user_id"]

    def __init__(self, score):
        score.pop("user", {})
        super().__init__(score, self.table, self.key_columns, self.flatten_columns, self.json_columns, self.column_list)