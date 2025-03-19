import json
from util.jsonDataObject import jsonDataObject


class Beatmap(jsonDataObject):
    table = "beatmap"  # Hardcoded table name
    key_columns = "id"
    flatten_columns = {"beatmapset_hype"}
    json_columns = {"beatmapset_covers", 
                    "beatmapset_nominations_summary",
                    "beatmapset_availability", 
                    "beatmapset_ratings", 
                    "failtimes", 
                    "owners"}

    def __init__(self, beatmap):
        beatmapset = beatmap.pop("beatmapset", {})
        if isinstance(beatmapset, dict):
            for key, value in beatmapset.items():
                beatmap[f"beatmapset_{key}"] = value
        
        super().__init__(beatmap, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
