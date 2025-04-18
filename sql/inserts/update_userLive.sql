truncate table userLive;

insert
	into
	public.userlive
(user_id,
	username,
	country_code,
	country_name,
	osu_count_100,
	osu_count_300,
	osu_count_50,
	osu_count_miss,
	osu_global_rank,
	osu_grade_counts_a,
	osu_grade_counts_s,
	osu_grade_counts_sh,
	osu_grade_counts_ss,
	osu_grade_counts_ssh,
	osu_hit_accuracy,
	osu_level_current,
	osu_level_progress,
	osu_maximum_combo,
	osu_play_count,
	osu_play_time,
	osu_pp,
	osu_ranked_score,
	osu_replays_watched_by_others,
	osu_total_hits,
	osu_total_score,
	taiko_count_100,
	taiko_count_300,
	taiko_count_50,
	taiko_count_miss,
	taiko_global_rank,
	taiko_grade_counts_a,
	taiko_grade_counts_s,
	taiko_grade_counts_sh,
	taiko_grade_counts_ss,
	taiko_grade_counts_ssh,
	taiko_hit_accuracy,
	taiko_level_current,
	taiko_level_progress,
	taiko_maximum_combo,
	taiko_play_count,
	taiko_play_time,
	taiko_pp,
	taiko_ranked_score,
	taiko_replays_watched_by_others,
	taiko_total_hits,
	taiko_total_score,
	fruits_count_100,
	fruits_count_300,
	fruits_count_50,
	fruits_count_miss,
	fruits_global_rank,
	fruits_grade_counts_a,
	fruits_grade_counts_s,
	fruits_grade_counts_sh,
	fruits_grade_counts_ss,
	fruits_grade_counts_ssh,
	fruits_hit_accuracy,
	fruits_level_current,
	fruits_level_progress,
	fruits_maximum_combo,
	fruits_play_count,
	fruits_play_time,
	fruits_pp,
	fruits_ranked_score,
	fruits_replays_watched_by_others,
	fruits_total_hits,
	fruits_total_score,
	mania_count_100,
	mania_count_300,
	mania_count_50,
	mania_count_miss,
	mania_global_rank,
	mania_grade_counts_a,
	mania_grade_counts_s,
	mania_grade_counts_sh,
	mania_grade_counts_ss,
	mania_grade_counts_ssh,
	mania_hit_accuracy,
	mania_level_current,
	mania_level_progress,
	mania_maximum_combo,
	mania_play_count,
	mania_play_time,
	mania_pp,
	mania_ranked_score,
	mania_replays_watched_by_others,
	mania_total_hits,
	mania_total_score,
	team_flag_url,
	team_id,
	team_name,
	team_short_name)
select
	uo.id,
	uo.username,
	uo.country_code,
	uo.country_name,
	osu_count_100,
	osu_count_300,
	osu_count_50,
	osu_count_miss,
	osu_global_rank,
	osu_grade_counts_a,
	osu_grade_counts_s,
	osu_grade_counts_sh,
	osu_grade_counts_ss,
	osu_grade_counts_ssh,
	osu_hit_accuracy,
	osu_level_current,
	osu_level_progress,
	osu_maximum_combo,
	osu_play_count,
	osu_play_time,
	osu_pp,
	osu_ranked_score,
	osu_replays_watched_by_others,
	osu_total_hits,
	osu_total_score,
	taiko_count_100,
	taiko_count_300,
	taiko_count_50,
	taiko_count_miss,
	taiko_global_rank,
	taiko_grade_counts_a,
	taiko_grade_counts_s,
	taiko_grade_counts_sh,
	taiko_grade_counts_ss,
	taiko_grade_counts_ssh,
	taiko_hit_accuracy,
	taiko_level_current,
	taiko_level_progress,
	taiko_maximum_combo,
	taiko_play_count,
	taiko_play_time,
	taiko_pp,
	taiko_ranked_score,
	taiko_replays_watched_by_others,
	taiko_total_hits,
	taiko_total_score,
	fruits_count_100,
	fruits_count_300,
	fruits_count_50,
	fruits_count_miss,
	fruits_global_rank,
	fruits_grade_counts_a,
	fruits_grade_counts_s,
	fruits_grade_counts_sh,
	fruits_grade_counts_ss,
	fruits_grade_counts_ssh,
	fruits_hit_accuracy,
	fruits_level_current,
	fruits_level_progress,
	fruits_maximum_combo,
	fruits_play_count,
	fruits_play_time,
	fruits_pp,
	fruits_ranked_score,
	fruits_replays_watched_by_others,
	fruits_total_hits,
	fruits_total_score,
	mania_count_100,
	mania_count_300,
	mania_count_50,
	mania_count_miss,
	mania_global_rank,
	mania_grade_counts_a,
	mania_grade_counts_s,
	mania_grade_counts_sh,
	mania_grade_counts_ss,
	mania_grade_counts_ssh,
	mania_hit_accuracy,
	mania_level_current,
	mania_level_progress,
	mania_maximum_combo,
	mania_play_count,
	mania_play_time,
	mania_pp,
	mania_ranked_score,
	mania_replays_watched_by_others,
	mania_total_hits,
	mania_total_score,
	uo.team_flag_url,
	uo.team_id,
	uo.team_name,
	uo.team_short_name
from
	userOsu uo
full join userTaiko ut on
	uo.id = ut.id
full join userFruits uf on
	uo.id = uf.id
full join userMania um on
	uo.id = um.id
where uo.id in (6245906);