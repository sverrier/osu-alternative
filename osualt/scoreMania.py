import json
from osualt.jsonDataObject import jsonDataObject

class ScoreMania(jsonDataObject):
    table = "scoreMania"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"mods", "current_user_attributes"}  # JSONB fields
    flatten_columns = {"statistics", "maximum_statistics"}  # Flattened fields

    def __init__(self, score):
        score.pop("user", {})
        super().__init__(score, self.table, self.key_columns, self.flatten_columns, self.json_columns)