import json
from util.jsonDataObject import jsonDataObject


class UserFruits(jsonDataObject):
    table = "userFruits"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "fruits_level", "fruits_grade_counts"}

    def __init__(self, user):

        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value
        
            for key, value in user.pop("fruits", {}).items():
                user[f"fruits_{key}"] = value

            user.pop("taiko", None)
            user.pop("osu", None)
            user.pop("mania", None)

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
