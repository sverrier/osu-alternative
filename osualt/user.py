import json
from osualt.jsonDataObject import jsonDataObject


class User(jsonDataObject):
    table = "userExtended"  # Hardcoded table name
    json_columns = {"playstyle", 
                    "profile_order", 
                    "badges", 
                    "monthly_playcounts", 
                    "previous_usernames", 
                    "replays_watched_counts", 
                    "user_achievements",
                    "rank_history", 
                    "statistics_level", 
                    "statistics_grade_counts", 
                    "statistics_rank", 
                    "account_history", 
                    "active_tournament_banners", 
                    "groups"}
    flatten_columns = {"country", "cover", "kudosu", "team",
                       "daily_challenge_user_stats", "rank_highest", "statistics"}

    def __init__(self, user):
        user.pop("page", {})
        user.pop("rankHistory", {})
        super().__init__(user, self.table, self.flatten_columns,
                         self.json_columns)
