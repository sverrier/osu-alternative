import json
from osualt.jsonDataObject import jsonDataObject


class UserOsu(jsonDataObject):
    table = "userOsu"  # Hardcoded table name
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "osu_level", "osu_grade_counts"}

    def __init__(self, user):

        for key, value in user.pop("statistics_rulesets", {}).items():
            user[f"{key}"] = value
        
        for key, value in user.pop("osu", {}).items():
            user[f"osu_{key}"] = value

        user.pop("fruits")
        user.pop("taiko")
        user.pop("mania")

        super().__init__(user, self.table, self.flatten_columns,
                         self.json_columns)
