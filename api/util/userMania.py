import json
from util.jsonDataObject import jsonDataObject


class UserMania(jsonDataObject):
    table = "userMania"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "mania_level", "mania_grade_counts"}

    def __init__(self, user):

        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value
        
            for key, value in user.pop("mania", {}).items():
                user[f"mania_{key}"] = value

            user.pop("taiko", None)
            user.pop("osu", None)
            user.pop("fruits", None)

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
