import json
from osualt.jsonDataObject import jsonDataObject

class Score(jsonDataObject):
    table = "scores"  # Hardcoded table name
    json_columns = {"mods", "current_user_attributes", "user_country", "user_cover"}  # JSONB fields
    flatten_columns = {"statistics", "maximum_statistics", "user"}  # Flattened fields
    ignore_columns = {}

    def __init__(self, user):
        super().__init__(user, self.table, self.flatten_columns, self.json_columns, self.ignore_columns)