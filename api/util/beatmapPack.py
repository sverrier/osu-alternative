import json
from .jsonDataObject import jsonDataObject


class BeatmapPack(jsonDataObject):
    table = "beatmapPack"  # Hardcoded table name
    key_columns = "tag"
    flatten_columns = {}
    json_columns = {}
    date_columns = {"pack_date"}
    column_list = ["tag", "name", "author", "pack_date", "url", "no_diff_reduction", "ruleset_id", "beatmapset_ids"]

    def __init__(self, beatmapsets):
        beatmapsets.pop("user_completion_data")
        sets= beatmapsets.pop("beatmapsets", [])
        beatmapsets["pack_date"] = beatmapsets.pop("date")

        ids = []
        for bm in sets:
            ids.append(int(bm.get("id")))

        beatmapsets["beatmapset_ids"] = ids
        
        super().__init__(beatmapsets, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns, self.column_list)
