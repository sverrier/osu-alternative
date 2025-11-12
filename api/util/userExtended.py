import json
from .jsonDataObject import jsonDataObject


class UserExtended(jsonDataObject):
    table = "userExtended"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"playstyle", 
                    "profile_order", 
                    "badges", 
                    "current_season_stats", 
                    "monthly_playcounts", 
                    "previous_usernames", 
                    "replays_watched_counts", 
                    "user_achievements",
                    "rank_history", 
                    "account_history", 
                    "active_tournament_banners", 
                    "groups"}
    flatten_columns = {"country", "cover", "kudosu", "team",
                       "daily_challenge_user_stats", "rank_highest", 
                       "statistics_level", "statistics_grade_counts", "statistics_rank"}

    def __init__(self, user):
        user.pop("page", {})
        user.pop("rankHistory", {})
        
        for key, value in user.pop("statistics", {}).items():
            user[f"statistics_{key}"] = value

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
