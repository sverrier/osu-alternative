import json
from util.jsonDataObject import jsonDataObject


class UserOsu(jsonDataObject):
    table = "userOsu"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "osu_level", "osu_grade_counts"}

    def __init__(self, user):

        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value

                
            for key, value in user.pop("osu", {}).items():
                user[f"osu_{key}"] = value

            user.pop("taiko", None)
            user.pop("fruits", None)
            user.pop("mania", None)

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
