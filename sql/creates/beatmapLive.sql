CREATE TABLE IF NOT EXISTS public.beatmaplive (
	beatmap_id int4 NOT NULL,
	user_id int4 NULL,
	beatmapset_id int4 NULL,
	"mode" int4 NULL,
	status text NULL,
	stars numeric NULL,
	od numeric NULL,
	ar numeric NULL,
	bpm numeric NULL,
	cs numeric NULL,
	hp numeric NULL,
	length int4 NULL,
	drain_time int4 NULL,
	count_circles int4 NULL,
	count_sliders int4 NULL,
	count_spinners int4 NULL,
	max_combo int4 NULL,
	pass_count int4 NULL,
	play_count int4 NULL,
	fc_count int4 NULL,
	ss_count int4 NULL,
	favourite_count int4 NULL,
	ranked_date timestamptz NULL,
	submitted_date timestamptz NULL,
	last_updated timestamptz NULL,
	"version" text NULL,
	title text NULL,
	artist text NULL,
	"source" text NULL,
	tags text NULL,
	checksum text NULL,
	track_id int4 NULL,
	pack varchar NULL,
	lchg_time timestamp DEFAULT now() NULL,
	mapper text NULL,
	is_nsfw bool NULL,
	beatmap_offset int4 NULL,
	rating numeric NULL,
	is_spotlight bool NULL,
	genre int4 NULL,
	"language" int4 NULL,
	has_video bool NULL,
	has_storyboard bool NULL,
	download_disabled bool NULL,
	CONSTRAINT beatmaplive_pkey PRIMARY KEY (beatmap_id)
);

-- Table Triggers
DROP TRIGGER IF EXISTS trg_update_lchg_time_beatmaplive ON public.beatmaplive;

create trigger trg_update_lchg_time_beatmaplive before
update
    on
    public.beatmaplive for each row execute function update_lchg_time();