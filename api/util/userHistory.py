import json
from util.jsonDataObject import jsonDataObject
from datetime import datetime


class UserHistory(jsonDataObject):
    table = "userHistory"  # Hardcoded table name
    key_columns = "id,record_date"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "osu_level", "osu_grade_counts",
                       "taiko_level", "taiko_grade_counts",
                       "fruits_level", "fruits_grade_counts",
                       "mania_level", "mania_grade_counts"}

    included_columns = {'id', 'record_date', 'username', 'post_count', 'beatmap_playcounts_count', 'comments_count',
                        'favourite_beatmapset_count', 'follower_count', 'graveyard_beatmapset_count', 'guest_beatmapset_count',
                        'loved_beatmapset_count', 'mapping_follower_count', 'nominated_beatmapset_count', 'pending_beatmapset_count',
                        'ranked_beatmapset_count', 'ranked_and_approved_beatmapset_count', 'unranked_beatmapset_count', 'osu_count_100',
                        'osu_count_300', 'osu_count_50', 'osu_count_miss', 'osu_global_rank', 'osu_global_rank_exp',
                        'osu_pp', 'osu_pp_exp', 'osu_ranked_score', 'osu_hit_accuracy', 'osu_play_count', 'osu_play_time',
                        'osu_total_score', 'osu_total_hits', 'osu_maximum_combo', 'osu_replays_watched_by_others',
                        'osu_is_ranked', 'osu_country_rank', 'osu_grade_counts_ss', 'osu_grade_counts_ssh',
                        'osu_grade_counts_s', 'osu_grade_counts_sh', 'osu_grade_counts_a', 'taiko_count_100',
                        'taiko_count_300', 'taiko_count_50', 'taiko_count_miss', 'taiko_global_rank',
                        'taiko_global_rank_exp', 'taiko_pp', 'taiko_pp_exp', 'taiko_ranked_score', 'taiko_hit_accuracy',
                        'taiko_play_count', 'taiko_play_time', 'taiko_total_score', 'taiko_total_hits',
                        'taiko_maximum_combo', 'taiko_replays_watched_by_others', 'taiko_is_ranked',
                        'taiko_country_rank', 'taiko_grade_counts_ss', 'taiko_grade_counts_ssh', 'taiko_grade_counts_s',
                        'taiko_grade_counts_sh', 'taiko_grade_counts_a', 'fruits_count_100', 'fruits_count_300',
                        'fruits_count_50', 'fruits_count_miss', 'fruits_global_rank', 'fruits_global_rank_exp',
                        'fruits_pp', 'fruits_pp_exp', 'fruits_ranked_score', 'fruits_hit_accuracy', 'fruits_play_count',
                        'fruits_play_time', 'fruits_total_score', 'fruits_total_hits', 'fruits_maximum_combo',
                        'fruits_replays_watched_by_others', 'fruits_is_ranked', 'fruits_country_rank',
                        'fruits_grade_counts_ss', 'fruits_grade_counts_ssh', 'fruits_grade_counts_s',
                        'fruits_grade_counts_sh', 'fruits_grade_counts_a', 'mania_count_100', 'mania_count_300',
                        'mania_count_50', 'mania_count_miss', 'mania_global_rank', 'mania_global_rank_exp', 'mania_pp',
                        'mania_pp_exp', 'mania_ranked_score', 'mania_hit_accuracy', 'mania_play_count', 'mania_play_time',
                        'mania_total_score', 'mania_total_hits', 'mania_maximum_combo', 'mania_replays_watched_by_others',
                        'mania_is_ranked', 'mania_country_rank', 'mania_grade_counts_ss', 'mania_grade_counts_ssh',
                        'mania_grade_counts_s', 'mania_grade_counts_sh', 'mania_grade_counts_a', 'kudosu_available',
                        'kudosu_total'}

    def __init__(self, user):

        user["record_date"] = datetime.today().strftime('%Y-%m-%d')
        
        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value

                
            for key, value in user.pop("osu", {}).items():
                user[f"osu_{key}"] = value

            for key, value in user.pop("fruits", {}).items():
                user[f"fruits_{key}"] = value
                
            for key, value in user.pop("taiko", {}).items():
                user[f"taiko_{key}"] = value
                
            for key, value in user.pop("mania", {}).items():
                user[f"mania_{key}"] = value
            
        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)

    def generate_insert_query(self):
        self.final_json = {key: value for key, value in self.final_json.items() if key in self.included_columns}
        return super().generate_insert_query()
