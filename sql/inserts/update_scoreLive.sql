insert
	into
	scoreLive (
	id,
	beatmap_id,
	user_id,
	accuracy,
	best_id,
	build_id,
	classic_total_score,
	ended_at,
	has_replay,
	is_perfect_combo,
	legacy_perfect,
	legacy_score_id,
	legacy_total_score,
	max_combo,
	maximum_statistics_great,
	maximum_statistics_ignore_hit,
	maximum_statistics_slider_tail_hit,
	maximum_statistics_legacy_combo_increase,
	maximum_statistics_large_bonus,
	maximum_statistics_large_tick_hit,
	maximum_statistics_small_bonus,
	mods,
	passed,
	pp,
	"preserve",
	processed,
	"rank",
	ranked,
	replay,
	ruleset_id,
	started_at,
	statistics_great,
	statistics_ok,
	statistics_meh,
	statistics_miss,
	statistics_ignore_hit,
	statistics_ignore_miss,
	statistics_slider_tail_hit,
	statistics_slider_tail_miss,
	statistics_large_bonus,
	statistics_large_tick_hit,
	statistics_large_tick_miss,
	statistics_small_bonus,
	total_score,
	total_score_without_mods,
	"type",
	statistics_small_tick_hit,
	statistics_small_tick_miss,
	maximum_statistics_small_tick_hit,
	highest_score
)
select
	id,
	beatmap_id,
	so.user_id,
	accuracy,
	best_id,
	build_id,
	classic_total_score,
	ended_at,
	has_replay,
	is_perfect_combo,
	legacy_perfect,
	legacy_score_id,
	legacy_total_score,
	max_combo,
	maximum_statistics_great,
	maximum_statistics_ignore_hit,
	maximum_statistics_slider_tail_hit,
	maximum_statistics_legacy_combo_increase,
	maximum_statistics_large_bonus,
	maximum_statistics_large_tick_hit,
	maximum_statistics_small_bonus,
	mods,
	passed,
	pp,
	"preserve",
	processed,
	"rank",
	ranked,
	replay,
	ruleset_id,
	started_at,
	statistics_great,
	statistics_ok,
	statistics_meh,
	statistics_miss,
	statistics_ignore_hit,
	statistics_ignore_miss,
	statistics_slider_tail_hit,
	statistics_slider_tail_miss,
	statistics_large_bonus,
	statistics_large_tick_hit,
	statistics_large_tick_miss,
	statistics_small_bonus,
	total_score,
	total_score_without_mods,
	"type",
	statistics_small_tick_hit,
	statistics_small_tick_miss,
	maximum_statistics_small_tick_hit,
	highest_score
from
	scoreosu so
inner join userLive ul on
	so.user_id = ul.user_id
on
	conflict do nothing;

insert into scoreLive (
	accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_great, maximum_statistics_large_bonus, maximum_statistics_small_bonus, maximum_statistics_ignore_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_great, statistics_ok, statistics_miss, statistics_large_bonus, statistics_ignore_hit, statistics_ignore_miss, statistics_small_bonus, total_score, total_score_without_mods, "type", user_id, maximum_statistics_legacy_combo_increase
)
SELECT accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_great, maximum_statistics_large_bonus, maximum_statistics_small_bonus, maximum_statistics_ignore_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_great, statistics_ok, statistics_miss, statistics_large_bonus, statistics_ignore_hit, statistics_ignore_miss, statistics_small_bonus, total_score, total_score_without_mods, "type", so.user_id, maximum_statistics_legacy_combo_increase
FROM public.scoretaiko so 
		inner join userLive ul on so.user_id = ul.user_id
on conflict do nothing;

insert into scoreLive (
	accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_legacy_combo_increase, maximum_statistics_perfect, maximum_statistics_ignore_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_combo_break, statistics_perfect, statistics_great, statistics_good, statistics_ok, statistics_meh, statistics_miss, statistics_ignore_hit, statistics_ignore_miss, total_score, total_score_without_mods, "type", user_id
)
SELECT accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_legacy_combo_increase, maximum_statistics_perfect, maximum_statistics_ignore_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_combo_break, statistics_perfect, statistics_great, statistics_good, statistics_ok, statistics_meh, statistics_miss, statistics_ignore_hit, statistics_ignore_miss, total_score, total_score_without_mods, "type", so.user_id
FROM public.scoremania so 
		inner join userLive ul on so.user_id = ul.user_id
on conflict do nothing;

insert into scoreLive (
 accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_great, maximum_statistics_ignore_hit, maximum_statistics_ignore_miss, maximum_statistics_large_bonus, maximum_statistics_large_tick_hit, maximum_statistics_small_tick_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_great, statistics_miss, statistics_ignore_hit, statistics_ignore_miss, statistics_large_bonus, statistics_large_tick_hit, statistics_large_tick_miss, statistics_small_tick_hit, statistics_small_tick_miss, total_score, total_score_without_mods, "type", user_id, maximum_statistics_legacy_combo_increase, maximum_statistics_miss
)
SELECT accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at, has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id, legacy_total_score, max_combo, maximum_statistics_great, maximum_statistics_ignore_hit, maximum_statistics_ignore_miss, maximum_statistics_large_bonus, maximum_statistics_large_tick_hit, maximum_statistics_small_tick_hit, mods, passed, pp, "preserve", processed, "rank", ranked, replay, ruleset_id, started_at, statistics_great, statistics_miss, statistics_ignore_hit, statistics_ignore_miss, statistics_large_bonus, statistics_large_tick_hit, statistics_large_tick_miss, statistics_small_tick_hit, statistics_small_tick_miss, total_score, total_score_without_mods, "type", so.user_id, maximum_statistics_legacy_combo_increase, maximum_statistics_miss
FROM public.scorefruits so 
		inner join userLive ul on so.user_id = ul.user_id
on conflict do nothing;