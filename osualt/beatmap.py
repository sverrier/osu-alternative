import json
from osualt.jsonDataObject import jsonDataObject


class Beatmap(jsonDataObject):
    table = "beatmaps"  # Hardcoded table name
    flatten_columns = {"beatmapset"}
    json_columns = {"beatmapset_covers", 
                    "beatmapset_nominations_summary",
                    "beatmapset_availability", 
                    "beatmapset_ratings", 
                    "failtimes", 
                    "owners"}

    def __init__(self, beatmap):
        super().__init__(beatmap, self.table, self.flatten_columns,
                         self.json_columns)
