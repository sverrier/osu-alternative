import json
from util.jsonDataObject import jsonDataObject


class UserMaster(jsonDataObject):
    table = "userMaster"  # Hardcoded table name
    key_columns = "id"
    json_columns = {"groups"}
    flatten_columns = {"country", "cover", "team",
                       "osu_level", "osu_grade_counts",
                       "taiko_level", "taiko_grade_counts",
                       "fruits_level", "fruits_grade_counts",
                       "mania_level", "mania_grade_counts"}
    included_columns = {"id","avatar_url","cover_custom_url","cover_id","cover_url","country_code","country_name",
                        "default_group","groups","is_active","is_bot","is_deleted","is_online","is_supporter",
                        "last_visit","osu_count_100","osu_count_300","osu_count_50","osu_count_miss",
                        "osu_global_rank","osu_global_rank_exp","osu_grade_counts_a","osu_grade_counts_s",
                        "osu_grade_counts_sh","osu_grade_counts_ss","osu_grade_counts_ssh","osu_hit_accuracy",
                        "osu_is_ranked","osu_level_current","osu_level_progress","osu_maximum_combo","osu_play_count",
                        "osu_play_time","osu_pp","osu_pp_exp","osu_ranked_score","osu_replays_watched_by_others",
                        "osu_total_hits","osu_total_score","taiko_count_100","taiko_count_300","taiko_count_50",
                        "taiko_count_miss","taiko_global_rank","taiko_global_rank_exp","taiko_grade_counts_a",
                        "taiko_grade_counts_s","taiko_grade_counts_sh","taiko_grade_counts_ss","taiko_grade_counts_ssh",
                        "taiko_hit_accuracy","taiko_is_ranked","taiko_level_current","taiko_level_progress",
                        "taiko_maximum_combo","taiko_play_count","taiko_play_time","taiko_pp","taiko_pp_exp",
                        "taiko_ranked_score","taiko_replays_watched_by_others","taiko_total_hits","taiko_total_score",
                        "fruits_count_100","fruits_count_300","fruits_count_50","fruits_count_miss",
                        "fruits_global_rank","fruits_global_rank_exp","fruits_grade_counts_a","fruits_grade_counts_s",
                        "fruits_grade_counts_sh","fruits_grade_counts_ss","fruits_grade_counts_ssh",
                        "fruits_hit_accuracy","fruits_is_ranked","fruits_level_current","fruits_level_progress",
                        "fruits_maximum_combo","fruits_play_count","fruits_play_time","fruits_pp","fruits_pp_exp",
                        "fruits_ranked_score","fruits_replays_watched_by_others","fruits_total_hits",
                        "fruits_total_score","mania_count_100","mania_count_300","mania_count_50","mania_count_miss",
                        "mania_global_rank","mania_global_rank_exp","mania_grade_counts_a","mania_grade_counts_s",
                        "mania_grade_counts_sh","mania_grade_counts_ss","mania_grade_counts_ssh","mania_hit_accuracy",
                        "mania_is_ranked","mania_level_current","mania_level_progress","mania_maximum_combo",
                        "mania_play_count","mania_play_time","mania_pp","mania_pp_exp","mania_ranked_score",
                        "mania_replays_watched_by_others","mania_total_hits","mania_total_score","pm_friends_only",
                        "profile_colour","team_flag_url","team_id","team_name","team_short_name","username",
                        "registered"}

    def __init__(self, user):

        statistics_rulesets = user.pop("statistics_rulesets", {})
        if isinstance(statistics_rulesets, dict):
            for key, value in statistics_rulesets.items():
                user[f"{key}"] = value

                
            for key, value in user.pop("osu", {}).items():
                user[f"osu_{key}"] = value
            for key, value in user.pop("taiko", {}).items():
                user[f"taiko_{key}"] = value
            for key, value in user.pop("fruits", {}).items():
                user[f"fruits_{key}"] = value
            for key, value in user.pop("mania", {}).items():
                user[f"mania_{key}"] = value

        super().__init__(user, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns)
    def generate_insert_query(self):
        self.final_json = {key: value for key, value in self.final_json.items() if key in self.included_columns}
        return super().generate_insert_query()