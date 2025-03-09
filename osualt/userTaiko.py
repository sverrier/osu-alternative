import json
from osualt.jsonDataObject import jsonDataObject


class UserTaiko(jsonDataObject):
    table = "userTaiko"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "taiko_level", "taiko_grade_counts"}

    def __init__(self, user):

        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value
        
            for key, value in user.pop("taiko", {}).items():
                user[f"taiko_{key}"] = value

            user.pop("fruits", None)
            user.pop("osu", None)
            user.pop("mania", None)

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
