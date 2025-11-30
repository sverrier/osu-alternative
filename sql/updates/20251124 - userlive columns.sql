ALTER TABLE public.userLive
  ADD COLUMN IF NOT EXISTS osu_global_ss_rank     INTEGER,
  ADD COLUMN IF NOT EXISTS taiko_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS fruits_global_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS mania_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS total_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS osu_country_ss_rank    INTEGER,
  ADD COLUMN IF NOT EXISTS taiko_country_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS fruits_country_ss_rank INTEGER,
  ADD COLUMN IF NOT EXISTS mania_country_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS total_country_ss_rank  INTEGER;

ALTER TABLE public.usermaster
  ADD COLUMN IF NOT EXISTS osu_global_ss_rank     INTEGER,
  ADD COLUMN IF NOT EXISTS taiko_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS fruits_global_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS mania_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS total_global_ss_rank   INTEGER,
  ADD COLUMN IF NOT EXISTS osu_country_ss_rank    INTEGER,
  ADD COLUMN IF NOT EXISTS taiko_country_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS fruits_country_ss_rank INTEGER,
  ADD COLUMN IF NOT EXISTS mania_country_ss_rank  INTEGER,
  ADD COLUMN IF NOT EXISTS total_country_ss_rank  INTEGER;