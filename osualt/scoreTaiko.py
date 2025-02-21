import json
from osualt.jsonDataObject import jsonDataObject

class ScoreTaiko(jsonDataObject):
    table = "scoreTaiko"  # Hardcoded table name
    json_columns = {"mods", "current_user_attributes"}  # JSONB fields
    flatten_columns = {"statistics", "maximum_statistics"}  # Flattened fields

    def __init__(self, score):
        score.pop("user", {})
        super().__init__(score, self.table, self.flatten_columns, self.json_columns)