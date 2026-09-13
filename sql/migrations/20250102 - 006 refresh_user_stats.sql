CREATE OR REPLACE PROCEDURE public.refresh_user_grade_bcd_and_scores()
LANGUAGE plpgsql
AS $$
BEGIN
  -- 1) Aggregate from scoreLive -> per-user stats in a temp table
  DROP TABLE IF EXISTS tmp_user_bcd;
  CREATE TEMP TABLE tmp_user_bcd (
    user_id int8 PRIMARY KEY,

    osu_grade_counts_b   int4 NOT NULL DEFAULT 0,
    taiko_grade_counts_b int4 NOT NULL DEFAULT 0,
    fruits_grade_counts_b int4 NOT NULL DEFAULT 0,
    mania_grade_counts_b int4 NOT NULL DEFAULT 0,

    osu_grade_counts_c   int4 NOT NULL DEFAULT 0,
    taiko_grade_counts_c int4 NOT NULL DEFAULT 0,
    fruits_grade_counts_c int4 NOT NULL DEFAULT 0,
    mania_grade_counts_c int4 NOT NULL DEFAULT 0,

    osu_grade_counts_d   int4 NOT NULL DEFAULT 0,
    taiko_grade_counts_d int4 NOT NULL DEFAULT 0,
    fruits_grade_counts_d int4 NOT NULL DEFAULT 0,
    mania_grade_counts_d int4 NOT NULL DEFAULT 0,

    osu_normalized_score   int8 NOT NULL DEFAULT 0,
    taiko_normalized_score int8 NOT NULL DEFAULT 0,
    fruits_normalized_score int8 NOT NULL DEFAULT 0,
    mania_normalized_score int8 NOT NULL DEFAULT 0,

    medals_count int4 NOT NULL DEFAULT 0,
    badges_count int4 NOT NULL DEFAULT 0
  ) ON COMMIT DROP;

  INSERT INTO tmp_user_bcd (
    user_id,

    osu_grade_counts_b, taiko_grade_counts_b, fruits_grade_counts_b, mania_grade_counts_b,
    osu_grade_counts_c, taiko_grade_counts_c, fruits_grade_counts_c, mania_grade_counts_c,
    osu_grade_counts_d, taiko_grade_counts_d, fruits_grade_counts_d, mania_grade_counts_d,

    osu_normalized_score, taiko_normalized_score, fruits_normalized_score, mania_normalized_score
  )
  SELECT
    s.user_id_fk AS user_id,

    COUNT(*) FILTER (WHERE bm.mode = 0 AND UPPER(s.grade) = 'B')::int4 AS osu_grade_counts_b,
    COUNT(*) FILTER (WHERE bm.mode = 1 AND UPPER(s.grade) = 'B')::int4 AS taiko_grade_counts_b,
    COUNT(*) FILTER (WHERE bm.mode = 2 AND UPPER(s.grade) = 'B')::int4 AS fruits_grade_counts_b,
    COUNT(*) FILTER (WHERE bm.mode = 3 AND UPPER(s.grade) = 'B')::int4 AS mania_grade_counts_b,

    COUNT(*) FILTER (WHERE bm.mode = 0 AND UPPER(s.grade) = 'C')::int4 AS osu_grade_counts_c,
    COUNT(*) FILTER (WHERE bm.mode = 1 AND UPPER(s.grade) = 'C')::int4 AS taiko_grade_counts_c,
    COUNT(*) FILTER (WHERE bm.mode = 2 AND UPPER(s.grade) = 'C')::int4 AS fruits_grade_counts_c,
    COUNT(*) FILTER (WHERE bm.mode = 3 AND UPPER(s.grade) = 'C')::int4 AS mania_grade_counts_c,

    COUNT(*) FILTER (WHERE bm.mode = 0 AND UPPER(s.grade) = 'D')::int4 AS osu_grade_counts_d,
    COUNT(*) FILTER (WHERE bm.mode = 1 AND UPPER(s.grade) = 'D')::int4 AS taiko_grade_counts_d,
    COUNT(*) FILTER (WHERE bm.mode = 2 AND UPPER(s.grade) = 'D')::int4 AS fruits_grade_counts_d,
    COUNT(*) FILTER (WHERE bm.mode = 3 AND UPPER(s.grade) = 'D')::int4 AS mania_grade_counts_d,

    COALESCE(SUM(s.total_score) FILTER (WHERE bm.mode = 0), 0)::int8 AS osu_normalized_score,
    COALESCE(SUM(s.total_score) FILTER (WHERE bm.mode = 1), 0)::int8 AS taiko_normalized_score,
    COALESCE(SUM(s.total_score) FILTER (WHERE bm.mode = 2), 0)::int8 AS fruits_normalized_score,
    COALESCE(SUM(s.total_score) FILTER (WHERE bm.mode = 3), 0)::int8 AS mania_normalized_score
  FROM public.scoreLive s
  JOIN public.beatmapLive bm
    ON bm.beatmap_id = s.beatmap_id_fk
  WHERE s.highest_score = true
    AND bm.mode IN (0,1,2,3)
    AND s.ruleset_id = bm.mode
  GROUP BY s.user_id_fk;

  -- 2) Add medals/badges totals (JSON arrays) from userExtended
  UPDATE tmp_user_bcd t
  SET
    medals_count =
      COALESCE(
        CASE
          WHEN jsonb_typeof(ue.user_achievements) = 'array' THEN jsonb_array_length(ue.user_achievements)
          ELSE 0
        END, 0
      )::int4,
    badges_count =
      COALESCE(
        CASE
          WHEN jsonb_typeof(ue.badges) = 'array' THEN jsonb_array_length(ue.badges)
          ELSE 0
        END, 0
      )::int4
  FROM public.userExtended ue
  WHERE ue.id = t.user_id;

  -- 3) Update userMaster (only if changed)
  UPDATE public.userMaster um
  SET
    osu_grade_counts_b = t.osu_grade_counts_b,
    taiko_grade_counts_b = t.taiko_grade_counts_b,
    fruits_grade_counts_b = t.fruits_grade_counts_b,
    mania_grade_counts_b = t.mania_grade_counts_b,

    osu_grade_counts_c = t.osu_grade_counts_c,
    taiko_grade_counts_c = t.taiko_grade_counts_c,
    fruits_grade_counts_c = t.fruits_grade_counts_c,
    mania_grade_counts_c = t.mania_grade_counts_c,

    osu_grade_counts_d = t.osu_grade_counts_d,
    taiko_grade_counts_d = t.taiko_grade_counts_d,
    fruits_grade_counts_d = t.fruits_grade_counts_d,
    mania_grade_counts_d = t.mania_grade_counts_d,

    osu_normalized_score = t.osu_normalized_score,
    taiko_normalized_score = t.taiko_normalized_score,
    fruits_normalized_score = t.fruits_normalized_score,
    mania_normalized_score = t.mania_normalized_score,

    medals_count = t.medals_count,
    badges_count = t.badges_count
  FROM tmp_user_bcd t
  WHERE um.id = t.user_id
    AND (
      um.osu_grade_counts_b   IS DISTINCT FROM t.osu_grade_counts_b OR
      um.taiko_grade_counts_b IS DISTINCT FROM t.taiko_grade_counts_b OR
      um.fruits_grade_counts_b IS DISTINCT FROM t.fruits_grade_counts_b OR
      um.mania_grade_counts_b IS DISTINCT FROM t.mania_grade_counts_b OR

      um.osu_grade_counts_c   IS DISTINCT FROM t.osu_grade_counts_c OR
      um.taiko_grade_counts_c IS DISTINCT FROM t.taiko_grade_counts_c OR
      um.fruits_grade_counts_c IS DISTINCT FROM t.fruits_grade_counts_c OR
      um.mania_grade_counts_c IS DISTINCT FROM t.mania_grade_counts_c OR

      um.osu_grade_counts_d   IS DISTINCT FROM t.osu_grade_counts_d OR
      um.taiko_grade_counts_d IS DISTINCT FROM t.taiko_grade_counts_d OR
      um.fruits_grade_counts_d IS DISTINCT FROM t.fruits_grade_counts_d OR
      um.mania_grade_counts_d IS DISTINCT FROM t.mania_grade_counts_d OR

      um.osu_normalized_score   IS DISTINCT FROM t.osu_normalized_score OR
      um.taiko_normalized_score IS DISTINCT FROM t.taiko_normalized_score OR
      um.fruits_normalized_score IS DISTINCT FROM t.fruits_normalized_score OR
      um.mania_normalized_score IS DISTINCT FROM t.mania_normalized_score OR

      um.medals_count IS DISTINCT FROM t.medals_count OR
      um.badges_count IS DISTINCT FROM t.badges_count
    );

  -- 4) Update userLive (only if changed)
  UPDATE public.userLive ul
  SET
    osu_grade_counts_b = t.osu_grade_counts_b,
    taiko_grade_counts_b = t.taiko_grade_counts_b,
    fruits_grade_counts_b = t.fruits_grade_counts_b,
    mania_grade_counts_b = t.mania_grade_counts_b,

    osu_grade_counts_c = t.osu_grade_counts_c,
    taiko_grade_counts_c = t.taiko_grade_counts_c,
    fruits_grade_counts_c = t.fruits_grade_counts_c,
    mania_grade_counts_c = t.mania_grade_counts_c,

    osu_grade_counts_d = t.osu_grade_counts_d,
    taiko_grade_counts_d = t.taiko_grade_counts_d,
    fruits_grade_counts_d = t.fruits_grade_counts_d,
    mania_grade_counts_d = t.mania_grade_counts_d,

    osu_normalized_score = t.osu_normalized_score,
    taiko_normalized_score = t.taiko_normalized_score,
    fruits_normalized_score = t.fruits_normalized_score,
    mania_normalized_score = t.mania_normalized_score,

    medals_count = t.medals_count,
    badges_count = t.badges_count
  FROM tmp_user_bcd t
  WHERE ul.user_id = t.user_id
    AND (
      ul.osu_grade_counts_b   IS DISTINCT FROM t.osu_grade_counts_b OR
      ul.taiko_grade_counts_b IS DISTINCT FROM t.taiko_grade_counts_b OR
      ul.fruits_grade_counts_b IS DISTINCT FROM t.fruits_grade_counts_b OR
      ul.mania_grade_counts_b IS DISTINCT FROM t.mania_grade_counts_b OR

      ul.osu_grade_counts_c   IS DISTINCT FROM t.osu_grade_counts_c OR
      ul.taiko_grade_counts_c IS DISTINCT FROM t.taiko_grade_counts_c OR
      ul.fruits_grade_counts_c IS DISTINCT FROM t.fruits_grade_counts_c OR
      ul.mania_grade_counts_c IS DISTINCT FROM t.mania_grade_counts_c OR

      ul.osu_grade_counts_d   IS DISTINCT FROM t.osu_grade_counts_d OR
      ul.taiko_grade_counts_d IS DISTINCT FROM t.taiko_grade_counts_d OR
      ul.fruits_grade_counts_d IS DISTINCT FROM t.fruits_grade_counts_d OR
      ul.mania_grade_counts_d IS DISTINCT FROM t.mania_grade_counts_d OR

      ul.osu_normalized_score   IS DISTINCT FROM t.osu_normalized_score OR
      ul.taiko_normalized_score IS DISTINCT FROM t.taiko_normalized_score OR
      ul.fruits_normalized_score IS DISTINCT FROM t.fruits_normalized_score OR
      ul.mania_normalized_score IS DISTINCT FROM t.mania_normalized_score OR

      ul.medals_count IS DISTINCT FROM t.medals_count OR
      ul.badges_count IS DISTINCT FROM t.badges_count
    );

END;
$$;
