-- public.scorelive definition

-- Drop table

-- DROP TABLE public.scorelive;

CREATE TABLE IF NOT EXISTS public.scorelive (
	id int8 NOT NULL,
	beatmap_id int4 NOT NULL,
	user_id int4 NOT NULL,
	accuracy numeric NOT NULL,
	best_id int4 NULL,
	build_id int4 NULL,
	classic_total_score int8 NOT NULL,
	ended_at timestamptz NOT NULL,
	has_replay bool NOT NULL,
	is_perfect_combo bool NOT NULL,
	legacy_perfect bool NOT NULL,
	legacy_score_id int8 NULL,
	legacy_total_score int8 NOT NULL,
	max_combo int4 NOT NULL,
	maximum_statistics_perfect int4 NULL,
	maximum_statistics_great int4 NULL,
	maximum_statistics_miss int4 NULL,
	maximum_statistics_ignore_hit int4 NULL,
	maximum_statistics_ignore_miss int4 NULL,
	maximum_statistics_slider_tail_hit int4 NULL,
	maximum_statistics_legacy_combo_increase int4 NULL,
	maximum_statistics_large_bonus int4 NULL,
	maximum_statistics_large_tick_hit int4 NULL,
	maximum_statistics_small_bonus int4 NULL,
	maximum_statistics_small_tick_hit int4 NULL,
	mods jsonb NOT NULL,
	passed bool NOT NULL,
	pp numeric NULL,
	"preserve" bool NOT NULL,
	processed bool NOT NULL,
	grade varchar(3) NOT NULL,
	ranked bool NOT NULL,
	replay bool NOT NULL,
	ruleset_id int4 NOT NULL,
	started_at timestamptz NULL,
	statistics_perfect int4 NULL,
	statistics_great int4 NULL,
	statistics_good int4 NULL,
	statistics_ok int4 NULL,
	statistics_meh int4 NULL,
	statistics_miss int4 NULL,
	statistics_ignore_hit int4 NULL,
	statistics_ignore_miss int4 NULL,
	statistics_slider_tail_hit int4 NULL,
	statistics_slider_tail_miss int4 NULL,
	statistics_large_bonus int4 NULL,
	statistics_large_tick_hit int4 NULL,
	statistics_large_tick_miss int4 NULL,
	statistics_small_bonus int4 NULL,
	statistics_small_tick_hit int4 NULL,
	statistics_small_tick_miss int4 NULL,
	statistics_combo_break int4 NULL,
	total_score int8 NULL,
	total_score_without_mods int8 NULL,
	"type" varchar(50) NOT NULL,
	highest_score bool NULL,
	highest_pp bool NULL,
	CONSTRAINT scorelive_pkey PRIMARY KEY (id)
);
CREATE INDEX IF NOT EXISTS idx_scorelive_ended_at ON public.scorelive USING brin (ended_at);
CREATE INDEX IF NOT EXISTS idx_scorelive_highest_only ON public.scorelive USING btree (beatmap_id, user_id) WHERE (highest_score = true);
CREATE INDEX IF NOT EXISTS scorelive_beatmap ON public.scorelive USING btree (beatmap_id);
CREATE INDEX IF NOT EXISTS scorelive_score ON public.scorelive USING btree (beatmap_id, user_id, classic_total_score DESC);
CREATE INDEX IF NOT EXISTS scorelive_user ON public.scorelive USING btree (user_id);