import json
from util.jsonDataObject import jsonDataObject
from datetime import datetime


class UserHistory(jsonDataObject):
    table = "userHistory"  # Hardcoded table name
    key_columns = "id,record_date"
    json_columns = {"playstyle", 
                    "profile_order", 
                    "badges", 
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

    included_columns = {'id', 'record_date', 'username', 'post_count', 'beatmap_playcounts_count', 'comments_count', 
        'favourite_beatmapset_count', 'follower_count', 'graveyard_beatmapset_count', 
        'guest_beatmapset_count', 'loved_beatmapset_count', 'mapping_follower_count', 
        'nominated_beatmapset_count', 'pending_beatmapset_count', 'ranked_beatmapset_count', 
        'scores_best_count', 'scores_first_count', 'scores_pinned_count', 'scores_recent_count', 
        'ranked_and_approved_beatmapset_count', 'unranked_beatmapset_count', 'statistics_count_100', 
        'statistics_count_300', 'statistics_count_50', 'statistics_count_miss', 'statistics_global_rank', 
        'statistics_global_rank_exp', 'statistics_pp', 'statistics_pp_exp', 'statistics_ranked_score', 
        'statistics_hit_accuracy', 'statistics_play_count', 'statistics_play_time', 
        'statistics_total_score', 'statistics_total_hits', 'statistics_maximum_combo', 
        'statistics_replays_watched_by_others', 'statistics_is_ranked', 'statistics_country_rank', 
        'statistics_grade_counts_ss', 'statistics_grade_counts_ssh', 'statistics_grade_counts_s', 
        'statistics_grade_counts_sh', 'statistics_grade_counts_a', 'kudosu_available', 'kudosu_total', 
        'rank_highest_rank', 'rank_highest_updated_at', 'daily_challenge_user_stats_daily_streak_best', 
        'daily_challenge_user_stats_daily_streak_current', 'daily_challenge_user_stats_last_update', 
        'daily_challenge_user_stats_last_weekly_streak', 'daily_challenge_user_stats_playcount', 
        'daily_challenge_user_stats_top_10p_placements', 'daily_challenge_user_stats_top_50p_placements', 
        'daily_challenge_user_stats_user_id', 'daily_challenge_user_stats_weekly_streak_best', 
        'daily_challenge_user_stats_weekly_streak_current'}

    def __init__(self, user):
        
        for key, value in user.pop("statistics", {}).items():
            user[f"statistics_{key}"] = value

        user["record_date"] = datetime.today().strftime('%Y-%m-%d')

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)

    def generate_insert_query(self):
        self.final_json = {key: value for key, value in self.final_json.items() if key in self.columns}
        return super().generate_insert_query()