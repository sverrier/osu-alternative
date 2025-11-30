CREATE OR REPLACE PROCEDURE public.refresh_user_ranks()
LANGUAGE plpgsql
AS $$
BEGIN
  -- Compute ranks directly over usermaster (single pass).
  WITH base AS (
    SELECT
      um.id,
      um.country_code,
      COALESCE(um.osu_grade_counts_ss, 0)    + COALESCE(um.osu_grade_counts_ssh, 0)    AS osu_ss,
      COALESCE(um.taiko_grade_counts_ss, 0)  + COALESCE(um.taiko_grade_counts_ssh, 0)  AS taiko_ss,
      COALESCE(um.fruits_grade_counts_ss, 0) + COALESCE(um.fruits_grade_counts_ssh, 0) AS fruits_ss,
      COALESCE(um.mania_grade_counts_ss, 0)  + COALESCE(um.mania_grade_counts_ssh, 0)  AS mania_ss
    FROM public.usermaster um
  ),
  scored AS (
    SELECT
      b.*,
      (b.osu_ss + b.taiko_ss + b.fruits_ss + b.mania_ss) AS total_ss
    FROM base b
  ),
  ranks AS (
    SELECT
      s.id,
      DENSE_RANK() OVER (ORDER BY s.osu_ss    DESC) AS osu_global_ss_rank,
      DENSE_RANK() OVER (ORDER BY s.taiko_ss  DESC) AS taiko_global_ss_rank,
      DENSE_RANK() OVER (ORDER BY s.fruits_ss DESC) AS fruits_global_ss_rank,
      DENSE_RANK() OVER (ORDER BY s.mania_ss  DESC) AS mania_global_ss_rank,
      DENSE_RANK() OVER (ORDER BY s.total_ss  DESC) AS total_global_ss_rank,
      DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_ss    DESC) AS osu_country_ss_rank,
      DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_ss  DESC) AS taiko_country_ss_rank,
      DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_ss DESC) AS fruits_country_ss_rank,
      DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_ss  DESC) AS mania_country_ss_rank,
      DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_ss  DESC) AS total_country_ss_rank
    FROM scored s
  )
  -- Update usermaster in-place; skip rows with no change to reduce bloat.
  UPDATE public.usermaster um
  SET
    osu_global_ss_rank     = r.osu_global_ss_rank,
    taiko_global_ss_rank   = r.taiko_global_ss_rank,
    fruits_global_ss_rank  = r.fruits_global_ss_rank,
    mania_global_ss_rank   = r.mania_global_ss_rank,
    total_global_ss_rank   = r.total_global_ss_rank,
    osu_country_ss_rank    = r.osu_country_ss_rank,
    taiko_country_ss_rank  = r.taiko_country_ss_rank,
    fruits_country_ss_rank = r.fruits_country_ss_rank,
    mania_country_ss_rank  = r.mania_country_ss_rank,
    total_country_ss_rank  = r.total_country_ss_rank
  FROM ranks r
  WHERE r.id = um.id
    AND (
      um.osu_global_ss_rank     IS DISTINCT FROM r.osu_global_ss_rank OR
      um.taiko_global_ss_rank   IS DISTINCT FROM r.taiko_global_ss_rank OR
      um.fruits_global_ss_rank  IS DISTINCT FROM r.fruits_global_ss_rank OR
      um.mania_global_ss_rank   IS DISTINCT FROM r.mania_global_ss_rank OR
      um.total_global_ss_rank   IS DISTINCT FROM r.total_global_ss_rank OR
      um.osu_country_ss_rank    IS DISTINCT FROM r.osu_country_ss_rank OR
      um.taiko_country_ss_rank  IS DISTINCT FROM r.taiko_country_ss_rank OR
      um.fruits_country_ss_rank IS DISTINCT FROM r.fruits_country_ss_rank OR
      um.mania_country_ss_rank  IS DISTINCT FROM r.mania_country_ss_rank OR
      um.total_country_ss_rank  IS DISTINCT FROM r.total_country_ss_rank
    );

  -- Copy the now-current ranks down to userLive (subset); skip unchanged rows.
  UPDATE public.userLive ul
  SET
    osu_global_ss_rank     = um.osu_global_ss_rank,
    taiko_global_ss_rank   = um.taiko_global_ss_rank,
    fruits_global_ss_rank  = um.fruits_global_ss_rank,
    mania_global_ss_rank   = um.mania_global_ss_rank,
    total_global_ss_rank   = um.total_global_ss_rank,
    osu_country_ss_rank    = um.osu_country_ss_rank,
    taiko_country_ss_rank  = um.taiko_country_ss_rank,
    fruits_country_ss_rank = um.fruits_country_ss_rank,
    mania_country_ss_rank  = um.mania_country_ss_rank,
    total_country_ss_rank  = um.total_country_ss_rank
  FROM public.usermaster um
  WHERE um.id = ul.user_id
    AND (
      ul.osu_global_ss_rank     IS DISTINCT FROM um.osu_global_ss_rank OR
      ul.taiko_global_ss_rank   IS DISTINCT FROM um.taiko_global_ss_rank OR
      ul.fruits_global_ss_rank  IS DISTINCT FROM um.fruits_global_ss_rank OR
      ul.mania_global_ss_rank   IS DISTINCT FROM um.mania_global_ss_rank OR
      ul.total_global_ss_rank   IS DISTINCT FROM um.total_global_ss_rank OR
      ul.osu_country_ss_rank    IS DISTINCT FROM um.osu_country_ss_rank OR
      ul.taiko_country_ss_rank  IS DISTINCT FROM um.taiko_country_ss_rank OR
      ul.fruits_country_ss_rank IS DISTINCT FROM um.fruits_country_ss_rank OR
      ul.mania_country_ss_rank  IS DISTINCT FROM um.mania_country_ss_rank OR
      ul.total_country_ss_rank  IS DISTINCT FROM um.total_country_ss_rank
    );
END;
$$;