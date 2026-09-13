CREATE OR REPLACE PROCEDURE public.refresh_userliveranks()
LANGUAGE plpgsql
AS $$
BEGIN
  DROP TABLE IF EXISTS tmp_user_ranks;

  CREATE TEMP TABLE tmp_user_ranks ON COMMIT DROP AS
  WITH base AS (
    SELECT
      um.id AS user_id,
      um.country_code,

      /* ===== Grade counts ===== */
      (COALESCE(um.osu_grade_counts_ss, 0)    + COALESCE(um.osu_grade_counts_ssh, 0))    AS osu_ss,
      (COALESCE(um.taiko_grade_counts_ss, 0)  + COALESCE(um.taiko_grade_counts_ssh, 0))  AS taiko_ss,
      (COALESCE(um.fruits_grade_counts_ss, 0) + COALESCE(um.fruits_grade_counts_ssh, 0)) AS fruits_ss,
      (COALESCE(um.mania_grade_counts_ss, 0)  + COALESCE(um.mania_grade_counts_ssh, 0))  AS mania_ss,

      COALESCE(um.osu_grade_counts_s, 0)    AS osu_s,
      COALESCE(um.taiko_grade_counts_s, 0)  AS taiko_s,
      COALESCE(um.fruits_grade_counts_s, 0) AS fruits_s,
      COALESCE(um.mania_grade_counts_s, 0)  AS mania_s,

      COALESCE(um.osu_grade_counts_a, 0)    AS osu_a,
      COALESCE(um.taiko_grade_counts_a, 0)  AS taiko_a,
      COALESCE(um.fruits_grade_counts_a, 0) AS fruits_a,
      COALESCE(um.mania_grade_counts_a, 0)  AS mania_a,

      COALESCE(um.osu_grade_counts_b, 0)    AS osu_b,
      COALESCE(um.taiko_grade_counts_b, 0)  AS taiko_b,
      COALESCE(um.fruits_grade_counts_b, 0) AS fruits_b,
      COALESCE(um.mania_grade_counts_b, 0)  AS mania_b,

      COALESCE(um.osu_grade_counts_c, 0)    AS osu_c,
      COALESCE(um.taiko_grade_counts_c, 0)  AS taiko_c,
      COALESCE(um.fruits_grade_counts_c, 0) AS fruits_c,
      COALESCE(um.mania_grade_counts_c, 0)  AS mania_c,

      COALESCE(um.osu_grade_counts_d, 0)    AS osu_d,
      COALESCE(um.taiko_grade_counts_d, 0)  AS taiko_d,
      COALESCE(um.fruits_grade_counts_d, 0) AS fruits_d,
      COALESCE(um.mania_grade_counts_d, 0)  AS mania_d,

      /* ===== Score family =====
         - score => normalized_score (new)
         - classic_score => ranked_score (profile)
         - alternative_score => *_alternative_score (new)
      */
      COALESCE(um.osu_normalized_score, 0)    AS osu_score,
      COALESCE(um.taiko_normalized_score, 0)  AS taiko_score,
      COALESCE(um.fruits_normalized_score, 0) AS fruits_score,
      COALESCE(um.mania_normalized_score, 0)  AS mania_score,

      COALESCE(um.osu_ranked_score, 0)    AS osu_classic_score,
      COALESCE(um.taiko_ranked_score, 0)  AS taiko_classic_score,
      COALESCE(um.fruits_ranked_score, 0) AS fruits_classic_score,
      COALESCE(um.mania_ranked_score, 0)  AS mania_classic_score,

      COALESCE(um.osu_alternative_score, 0)    AS osu_alternative_score,
      COALESCE(um.taiko_alternative_score, 0)  AS taiko_alternative_score,
      COALESCE(um.fruits_alternative_score, 0) AS fruits_alternative_score,
      COALESCE(um.mania_alternative_score, 0)  AS mania_alternative_score,

      /* ===== Replays watched (rank totals only) ===== */
      COALESCE(um.osu_replays_watched_by_others, 0)    AS osu_replays_watched,
      COALESCE(um.taiko_replays_watched_by_others, 0)  AS taiko_replays_watched,
      COALESCE(um.fruits_replays_watched_by_others, 0) AS fruits_replays_watched,
      COALESCE(um.mania_replays_watched_by_others, 0)  AS mania_replays_watched,

      /* ===== Medals / badges are totals only ===== */
      COALESCE(um.medals_count, 0) AS total_medals,
      COALESCE(um.badges_count, 0) AS total_badges,

      /* ===== Playcount / playtime ===== */
      COALESCE(um.osu_play_count, 0)    AS osu_playcount,
      COALESCE(um.taiko_play_count, 0)  AS taiko_playcount,
      COALESCE(um.fruits_play_count, 0) AS fruits_playcount,
      COALESCE(um.mania_play_count, 0)  AS mania_playcount,

      COALESCE(um.osu_play_time, 0)    AS osu_playtime,
      COALESCE(um.taiko_play_time, 0)  AS taiko_playtime,
      COALESCE(um.fruits_play_time, 0) AS fruits_playtime,
      COALESCE(um.mania_play_time, 0)  AS mania_playtime
    FROM public.userMaster um
  ),
  scored AS (
    SELECT
      b.*,

      (b.osu_ss + b.taiko_ss + b.fruits_ss + b.mania_ss) AS total_ss,
      (b.osu_s  + b.taiko_s  + b.fruits_s  + b.mania_s)  AS total_s,
      (b.osu_a  + b.taiko_a  + b.fruits_a  + b.mania_a)  AS total_a,
      (b.osu_b  + b.taiko_b  + b.fruits_b  + b.mania_b)  AS total_b,
      (b.osu_c  + b.taiko_c  + b.fruits_c  + b.mania_c)  AS total_c,
      (b.osu_d  + b.taiko_d  + b.fruits_d  + b.mania_d)  AS total_d,

      (b.osu_score + b.taiko_score + b.fruits_score + b.mania_score) AS total_score,
      (b.osu_classic_score + b.taiko_classic_score + b.fruits_classic_score + b.mania_classic_score) AS total_classic_score,
      (b.osu_alternative_score + b.taiko_alternative_score + b.fruits_alternative_score + b.mania_alternative_score) AS total_alternative_score,

      (b.osu_replays_watched + b.taiko_replays_watched + b.fruits_replays_watched + b.mania_replays_watched) AS total_replays_watched,
      (b.osu_playcount + b.taiko_playcount + b.fruits_playcount + b.mania_playcount) AS total_playcount,
      (b.osu_playtime + b.taiko_playtime + b.fruits_playtime + b.mania_playtime) AS total_playtime
    FROM base b
  )
  SELECT
    s.user_id,

    /* ===== SS ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_ss DESC)    AS osu_global_ss_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_ss DESC)  AS taiko_global_ss_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_ss DESC) AS fruits_global_ss_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_ss DESC)  AS mania_global_ss_rank,
    DENSE_RANK() OVER (ORDER BY s.total_ss DESC)  AS total_global_ss_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_ss DESC)    AS osu_country_ss_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_ss DESC)  AS taiko_country_ss_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_ss DESC) AS fruits_country_ss_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_ss DESC)  AS mania_country_ss_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_ss DESC)  AS total_country_ss_rank,

    /* ===== S ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_s DESC)    AS osu_global_s_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_s DESC)  AS taiko_global_s_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_s DESC) AS fruits_global_s_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_s DESC)  AS mania_global_s_rank,
    DENSE_RANK() OVER (ORDER BY s.total_s DESC)  AS total_global_s_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_s DESC)    AS osu_country_s_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_s DESC)  AS taiko_country_s_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_s DESC) AS fruits_country_s_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_s DESC)  AS mania_country_s_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_s DESC)  AS total_country_s_rank,

    /* ===== A ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_a DESC)    AS osu_global_a_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_a DESC)  AS taiko_global_a_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_a DESC) AS fruits_global_a_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_a DESC)  AS mania_global_a_rank,
    DENSE_RANK() OVER (ORDER BY s.total_a DESC)  AS total_global_a_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_a DESC)    AS osu_country_a_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_a DESC)  AS taiko_country_a_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_a DESC) AS fruits_country_a_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_a DESC)  AS mania_country_a_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_a DESC)  AS total_country_a_rank,

    /* ===== B ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_b DESC)    AS osu_global_b_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_b DESC)  AS taiko_global_b_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_b DESC) AS fruits_global_b_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_b DESC)  AS mania_global_b_rank,
    DENSE_RANK() OVER (ORDER BY s.total_b DESC)  AS total_global_b_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_b DESC)    AS osu_country_b_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_b DESC)  AS taiko_country_b_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_b DESC) AS fruits_country_b_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_b DESC)  AS mania_country_b_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_b DESC)  AS total_country_b_rank,

    /* ===== C ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_c DESC)    AS osu_global_c_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_c DESC)  AS taiko_global_c_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_c DESC) AS fruits_global_c_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_c DESC)  AS mania_global_c_rank,
    DENSE_RANK() OVER (ORDER BY s.total_c DESC)  AS total_global_c_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_c DESC)    AS osu_country_c_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_c DESC)  AS taiko_country_c_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_c DESC) AS fruits_country_c_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_c DESC)  AS mania_country_c_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_c DESC)  AS total_country_c_rank,

    /* ===== D ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_d DESC)    AS osu_global_d_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_d DESC)  AS taiko_global_d_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_d DESC) AS fruits_global_d_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_d DESC)  AS mania_global_d_rank,
    DENSE_RANK() OVER (ORDER BY s.total_d DESC)  AS total_global_d_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_d DESC)    AS osu_country_d_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_d DESC)  AS taiko_country_d_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_d DESC) AS fruits_country_d_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_d DESC)  AS mania_country_d_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_d DESC)  AS total_country_d_rank,

    /* ===== SCORE (normalized) ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_score DESC)    AS osu_global_score_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_score DESC)  AS taiko_global_score_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_score DESC) AS fruits_global_score_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_score DESC)  AS mania_global_score_rank,
    DENSE_RANK() OVER (ORDER BY s.total_score DESC)  AS total_global_score_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_score DESC)    AS osu_country_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_score DESC)  AS taiko_country_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_score DESC) AS fruits_country_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_score DESC)  AS mania_country_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_score DESC)  AS total_country_score_rank,

    /* ===== CLASSIC SCORE (ranked_score) ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_classic_score DESC)    AS osu_global_classic_score_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_classic_score DESC)  AS taiko_global_classic_score_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_classic_score DESC) AS fruits_global_classic_score_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_classic_score DESC)  AS mania_global_classic_score_rank,
    DENSE_RANK() OVER (ORDER BY s.total_classic_score DESC)  AS total_global_classic_score_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_classic_score DESC)    AS osu_country_classic_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_classic_score DESC)  AS taiko_country_classic_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_classic_score DESC) AS fruits_country_classic_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_classic_score DESC)  AS mania_country_classic_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_classic_score DESC)  AS total_country_classic_score_rank,

    /* ===== ALTERNATIVE SCORE ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_alternative_score DESC)    AS osu_global_alternative_score_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_alternative_score DESC)  AS taiko_global_alternative_score_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_alternative_score DESC) AS fruits_global_alternative_score_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_alternative_score DESC)  AS mania_global_alternative_score_rank,
    DENSE_RANK() OVER (ORDER BY s.total_alternative_score DESC)  AS total_global_alternative_score_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_alternative_score DESC)    AS osu_country_alternative_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_alternative_score DESC)  AS taiko_country_alternative_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_alternative_score DESC) AS fruits_country_alternative_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_alternative_score DESC)  AS mania_country_alternative_score_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_alternative_score DESC)  AS total_country_alternative_score_rank,

    /* ===== REPLAYS ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_replays_watched DESC) AS osu_global_replays_watched_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_replays_watched DESC) AS taiko_global_replays_watched_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_replays_watched DESC) AS fruits_global_replays_watched_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_replays_watched DESC) AS mania_global_replays_watched_rank,
    DENSE_RANK() OVER (ORDER BY s.total_replays_watched DESC) AS total_global_replays_watched_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_replays_watched DESC) AS osu_country_replays_watched_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_replays_watched DESC) AS taiko_country_replays_watched_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_replays_watched DESC) AS fruits_country_replays_watched_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_replays_watched DESC) AS mania_country_replays_watched_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_replays_watched DESC) AS total_country_replays_watched_rank,

    DENSE_RANK() OVER (ORDER BY s.total_medals DESC) AS total_global_medals_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_medals DESC) AS total_country_medals_rank,

    DENSE_RANK() OVER (ORDER BY s.total_badges DESC) AS total_global_badges_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_badges DESC) AS total_country_badges_rank,

    /* ===== playcount/playtime ===== */
    DENSE_RANK() OVER (ORDER BY s.osu_playcount DESC)    AS osu_global_playcount_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_playcount DESC)  AS taiko_global_playcount_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_playcount DESC) AS fruits_global_playcount_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_playcount DESC)  AS mania_global_playcount_rank,
    DENSE_RANK() OVER (ORDER BY s.total_playcount DESC)  AS total_global_playcount_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_playcount DESC)    AS osu_country_playcount_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_playcount DESC)  AS taiko_country_playcount_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_playcount DESC) AS fruits_country_playcount_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_playcount DESC)  AS mania_country_playcount_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_playcount DESC)  AS total_country_playcount_rank,

    DENSE_RANK() OVER (ORDER BY s.osu_playtime DESC)    AS osu_global_playtime_rank,
    DENSE_RANK() OVER (ORDER BY s.taiko_playtime DESC)  AS taiko_global_playtime_rank,
    DENSE_RANK() OVER (ORDER BY s.fruits_playtime DESC) AS fruits_global_playtime_rank,
    DENSE_RANK() OVER (ORDER BY s.mania_playtime DESC)  AS mania_global_playtime_rank,
    DENSE_RANK() OVER (ORDER BY s.total_playtime DESC)  AS total_global_playtime_rank,

    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.osu_playtime DESC)    AS osu_country_playtime_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.taiko_playtime DESC)  AS taiko_country_playtime_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.fruits_playtime DESC) AS fruits_country_playtime_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.mania_playtime DESC)  AS mania_country_playtime_rank,
    DENSE_RANK() OVER (PARTITION BY s.country_code ORDER BY s.total_playtime DESC)  AS total_country_playtime_rank
  FROM scored s;

  CREATE INDEX ON tmp_user_ranks (user_id);

  INSERT INTO public.userliveranks (
    userliverank_id,
    lchg_time,

    osu_global_ss_rank, taiko_global_ss_rank, fruits_global_ss_rank, mania_global_ss_rank, total_global_ss_rank,
    osu_country_ss_rank, taiko_country_ss_rank, fruits_country_ss_rank, mania_country_ss_rank, total_country_ss_rank,

    osu_global_s_rank, taiko_global_s_rank, fruits_global_s_rank, mania_global_s_rank, total_global_s_rank,
    osu_country_s_rank, taiko_country_s_rank, fruits_country_s_rank, mania_country_s_rank, total_country_s_rank,

    osu_global_a_rank, taiko_global_a_rank, fruits_global_a_rank, mania_global_a_rank, total_global_a_rank,
    osu_country_a_rank, taiko_country_a_rank, fruits_country_a_rank, mania_country_a_rank, total_country_a_rank,

    osu_global_b_rank, taiko_global_b_rank, fruits_global_b_rank, mania_global_b_rank, total_global_b_rank,
    osu_country_b_rank, taiko_country_b_rank, fruits_country_b_rank, mania_country_b_rank, total_country_b_rank,

    osu_global_c_rank, taiko_global_c_rank, fruits_global_c_rank, mania_global_c_rank, total_global_c_rank,
    osu_country_c_rank, taiko_country_c_rank, fruits_country_c_rank, mania_country_c_rank, total_country_c_rank,

    osu_global_d_rank, taiko_global_d_rank, fruits_global_d_rank, mania_global_d_rank, total_global_d_rank,
    osu_country_d_rank, taiko_country_d_rank, fruits_country_d_rank, mania_country_d_rank, total_country_d_rank,

    osu_global_score_rank, taiko_global_score_rank, fruits_global_score_rank, mania_global_score_rank, total_global_score_rank,
    osu_country_score_rank, taiko_country_score_rank, fruits_country_score_rank, mania_country_score_rank, total_country_score_rank,

    osu_global_classic_score_rank, taiko_global_classic_score_rank, fruits_global_classic_score_rank, mania_global_classic_score_rank, total_global_classic_score_rank,
    osu_country_classic_score_rank, taiko_country_classic_score_rank, fruits_country_classic_score_rank, mania_country_classic_score_rank, total_country_classic_score_rank,

    osu_global_alternative_score_rank, taiko_global_alternative_score_rank, fruits_global_alternative_score_rank, mania_global_alternative_score_rank, total_global_alternative_score_rank,
    osu_country_alternative_score_rank, taiko_country_alternative_score_rank, fruits_country_alternative_score_rank, mania_country_alternative_score_rank, total_country_alternative_score_rank,

    osu_global_replays_watched_rank, taiko_global_replays_watched_rank, fruits_global_replays_watched_rank, mania_global_replays_watched_rank, total_global_replays_watched_rank, 
    osu_country_replays_watched_rank, taiko_country_replays_watched_rank, fruits_country_replays_watched_rank, mania_country_replays_watched_rank, total_country_replays_watched_rank,

    total_global_medals_rank, total_country_medals_rank,
    total_global_badges_rank, total_country_badges_rank,

    osu_global_playcount_rank, taiko_global_playcount_rank, fruits_global_playcount_rank, mania_global_playcount_rank, total_global_playcount_rank,
    osu_country_playcount_rank, taiko_country_playcount_rank, fruits_country_playcount_rank, mania_country_playcount_rank, total_country_playcount_rank,

    osu_global_playtime_rank, taiko_global_playtime_rank, fruits_global_playtime_rank, mania_global_playtime_rank, total_global_playtime_rank,
    osu_country_playtime_rank, taiko_country_playtime_rank, fruits_country_playtime_rank, mania_country_playtime_rank, total_country_playtime_rank
  )
  SELECT
    t.user_id,
    now(),

    t.osu_global_ss_rank, t.taiko_global_ss_rank, t.fruits_global_ss_rank, t.mania_global_ss_rank, t.total_global_ss_rank,
    t.osu_country_ss_rank, t.taiko_country_ss_rank, t.fruits_country_ss_rank, t.mania_country_ss_rank, t.total_country_ss_rank,

    t.osu_global_s_rank, t.taiko_global_s_rank, t.fruits_global_s_rank, t.mania_global_s_rank, t.total_global_s_rank,
    t.osu_country_s_rank, t.taiko_country_s_rank, t.fruits_country_s_rank, t.mania_country_s_rank, t.total_country_s_rank,

    t.osu_global_a_rank, t.taiko_global_a_rank, t.fruits_global_a_rank, t.mania_global_a_rank, t.total_global_a_rank,
    t.osu_country_a_rank, t.taiko_country_a_rank, t.fruits_country_a_rank, t.mania_country_a_rank, t.total_country_a_rank,

    t.osu_global_b_rank, t.taiko_global_b_rank, t.fruits_global_b_rank, t.mania_global_b_rank, t.total_global_b_rank,
    t.osu_country_b_rank, t.taiko_country_b_rank, t.fruits_country_b_rank, t.mania_country_b_rank, t.total_country_b_rank,

    t.osu_global_c_rank, t.taiko_global_c_rank, t.fruits_global_c_rank, t.mania_global_c_rank, t.total_global_c_rank,
    t.osu_country_c_rank, t.taiko_country_c_rank, t.fruits_country_c_rank, t.mania_country_c_rank, t.total_country_c_rank,

    t.osu_global_d_rank, t.taiko_global_d_rank, t.fruits_global_d_rank, t.mania_global_d_rank, t.total_global_d_rank,
    t.osu_country_d_rank, t.taiko_country_d_rank, t.fruits_country_d_rank, t.mania_country_d_rank, t.total_country_d_rank,

    t.osu_global_score_rank, t.taiko_global_score_rank, t.fruits_global_score_rank, t.mania_global_score_rank, t.total_global_score_rank,
    t.osu_country_score_rank, t.taiko_country_score_rank, t.fruits_country_score_rank, t.mania_country_score_rank, t.total_country_score_rank,

    t.osu_global_classic_score_rank, t.taiko_global_classic_score_rank, t.fruits_global_classic_score_rank, t.mania_global_classic_score_rank, t.total_global_classic_score_rank,
    t.osu_country_classic_score_rank, t.taiko_country_classic_score_rank, t.fruits_country_classic_score_rank, t.mania_country_classic_score_rank, t.total_country_classic_score_rank,

    t.osu_global_alternative_score_rank, t.taiko_global_alternative_score_rank, t.fruits_global_alternative_score_rank, t.mania_global_alternative_score_rank, t.total_global_alternative_score_rank,
    t.osu_country_alternative_score_rank, t.taiko_country_alternative_score_rank, t.fruits_country_alternative_score_rank, t.mania_country_alternative_score_rank, t.total_country_alternative_score_rank,

    t.osu_global_replays_watched_rank, t.taiko_global_replays_watched_rank, t.fruits_global_replays_watched_rank, t.mania_global_replays_watched_rank, t.total_global_replays_watched_rank, 
    t.osu_country_replays_watched_rank, t.taiko_country_replays_watched_rank, t.fruits_country_replays_watched_rank, t.mania_country_replays_watched_rank, t.total_country_replays_watched_rank,

    t.total_global_medals_rank, t.total_country_medals_rank,
    t.total_global_badges_rank, t.total_country_badges_rank,

    t.osu_global_playcount_rank, t.taiko_global_playcount_rank, t.fruits_global_playcount_rank, t.mania_global_playcount_rank, t.total_global_playcount_rank,
    t.osu_country_playcount_rank, t.taiko_country_playcount_rank, t.fruits_country_playcount_rank, t.mania_country_playcount_rank, t.total_country_playcount_rank,

    t.osu_global_playtime_rank, t.taiko_global_playtime_rank, t.fruits_global_playtime_rank, t.mania_global_playtime_rank, t.total_global_playtime_rank,
    t.osu_country_playtime_rank, t.taiko_country_playtime_rank, t.fruits_country_playtime_rank, t.mania_country_playtime_rank, t.total_country_playtime_rank
  FROM tmp_user_ranks t
  ON CONFLICT (userliverank_id) DO UPDATE
  SET
    lchg_time = now(),

    osu_global_ss_rank = EXCLUDED.osu_global_ss_rank,
    taiko_global_ss_rank = EXCLUDED.taiko_global_ss_rank,
    fruits_global_ss_rank = EXCLUDED.fruits_global_ss_rank,
    mania_global_ss_rank = EXCLUDED.mania_global_ss_rank,
    total_global_ss_rank = EXCLUDED.total_global_ss_rank,
    osu_country_ss_rank = EXCLUDED.osu_country_ss_rank,
    taiko_country_ss_rank = EXCLUDED.taiko_country_ss_rank,
    fruits_country_ss_rank = EXCLUDED.fruits_country_ss_rank,
    mania_country_ss_rank = EXCLUDED.mania_country_ss_rank,
    total_country_ss_rank = EXCLUDED.total_country_ss_rank,

    osu_global_s_rank = EXCLUDED.osu_global_s_rank,
    taiko_global_s_rank = EXCLUDED.taiko_global_s_rank,
    fruits_global_s_rank = EXCLUDED.fruits_global_s_rank,
    mania_global_s_rank = EXCLUDED.mania_global_s_rank,
    total_global_s_rank = EXCLUDED.total_global_s_rank,
    osu_country_s_rank = EXCLUDED.osu_country_s_rank,
    taiko_country_s_rank = EXCLUDED.taiko_country_s_rank,
    fruits_country_s_rank = EXCLUDED.fruits_country_s_rank,
    mania_country_s_rank = EXCLUDED.mania_country_s_rank,
    total_country_s_rank = EXCLUDED.total_country_s_rank,

    osu_global_a_rank = EXCLUDED.osu_global_a_rank,
    taiko_global_a_rank = EXCLUDED.taiko_global_a_rank,
    fruits_global_a_rank = EXCLUDED.fruits_global_a_rank,
    mania_global_a_rank = EXCLUDED.mania_global_a_rank,
    total_global_a_rank = EXCLUDED.total_global_a_rank,
    osu_country_a_rank = EXCLUDED.osu_country_a_rank,
    taiko_country_a_rank = EXCLUDED.taiko_country_a_rank,
    fruits_country_a_rank = EXCLUDED.fruits_country_a_rank,
    mania_country_a_rank = EXCLUDED.mania_country_a_rank,
    total_country_a_rank = EXCLUDED.total_country_a_rank,

    osu_global_b_rank = EXCLUDED.osu_global_b_rank,
    taiko_global_b_rank = EXCLUDED.taiko_global_b_rank,
    fruits_global_b_rank = EXCLUDED.fruits_global_b_rank,
    mania_global_b_rank = EXCLUDED.mania_global_b_rank,
    total_global_b_rank = EXCLUDED.total_global_b_rank,
    osu_country_b_rank = EXCLUDED.osu_country_b_rank,
    taiko_country_b_rank = EXCLUDED.taiko_country_b_rank,
    fruits_country_b_rank = EXCLUDED.fruits_country_b_rank,
    mania_country_b_rank = EXCLUDED.mania_country_b_rank,
    total_country_b_rank = EXCLUDED.total_country_b_rank,

    osu_global_c_rank = EXCLUDED.osu_global_c_rank,
    taiko_global_c_rank = EXCLUDED.taiko_global_c_rank,
    fruits_global_c_rank = EXCLUDED.fruits_global_c_rank,
    mania_global_c_rank = EXCLUDED.mania_global_c_rank,
    total_global_c_rank = EXCLUDED.total_global_c_rank,
    osu_country_c_rank = EXCLUDED.osu_country_c_rank,
    taiko_country_c_rank = EXCLUDED.taiko_country_c_rank,
    fruits_country_c_rank = EXCLUDED.fruits_country_c_rank,
    mania_country_c_rank = EXCLUDED.mania_country_c_rank,
    total_country_c_rank = EXCLUDED.total_country_c_rank,

    osu_global_d_rank = EXCLUDED.osu_global_d_rank,
    taiko_global_d_rank = EXCLUDED.taiko_global_d_rank,
    fruits_global_d_rank = EXCLUDED.fruits_global_d_rank,
    mania_global_d_rank = EXCLUDED.mania_global_d_rank,
    total_global_d_rank = EXCLUDED.total_global_d_rank,
    osu_country_d_rank = EXCLUDED.osu_country_d_rank,
    taiko_country_d_rank = EXCLUDED.taiko_country_d_rank,
    fruits_country_d_rank = EXCLUDED.fruits_country_d_rank,
    mania_country_d_rank = EXCLUDED.mania_country_d_rank,
    total_country_d_rank = EXCLUDED.total_country_d_rank,

    osu_global_score_rank = EXCLUDED.osu_global_score_rank,
    taiko_global_score_rank = EXCLUDED.taiko_global_score_rank,
    fruits_global_score_rank = EXCLUDED.fruits_global_score_rank,
    mania_global_score_rank = EXCLUDED.mania_global_score_rank,
    total_global_score_rank = EXCLUDED.total_global_score_rank,
    osu_country_score_rank = EXCLUDED.osu_country_score_rank,
    taiko_country_score_rank = EXCLUDED.taiko_country_score_rank,
    fruits_country_score_rank = EXCLUDED.fruits_country_score_rank,
    mania_country_score_rank = EXCLUDED.mania_country_score_rank,
    total_country_score_rank = EXCLUDED.total_country_score_rank,

    osu_global_classic_score_rank = EXCLUDED.osu_global_classic_score_rank,
    taiko_global_classic_score_rank = EXCLUDED.taiko_global_classic_score_rank,
    fruits_global_classic_score_rank = EXCLUDED.fruits_global_classic_score_rank,
    mania_global_classic_score_rank = EXCLUDED.mania_global_classic_score_rank,
    total_global_classic_score_rank = EXCLUDED.total_global_classic_score_rank,
    osu_country_classic_score_rank = EXCLUDED.osu_country_classic_score_rank,
    taiko_country_classic_score_rank = EXCLUDED.taiko_country_classic_score_rank,
    fruits_country_classic_score_rank = EXCLUDED.fruits_country_classic_score_rank,
    mania_country_classic_score_rank = EXCLUDED.mania_country_classic_score_rank,
    total_country_classic_score_rank = EXCLUDED.total_country_classic_score_rank,

    osu_global_alternative_score_rank = EXCLUDED.osu_global_alternative_score_rank,
    taiko_global_alternative_score_rank = EXCLUDED.taiko_global_alternative_score_rank,
    fruits_global_alternative_score_rank = EXCLUDED.fruits_global_alternative_score_rank,
    mania_global_alternative_score_rank = EXCLUDED.mania_global_alternative_score_rank,
    total_global_alternative_score_rank = EXCLUDED.total_global_alternative_score_rank,
    osu_country_alternative_score_rank = EXCLUDED.osu_country_alternative_score_rank,
    taiko_country_alternative_score_rank = EXCLUDED.taiko_country_alternative_score_rank,
    fruits_country_alternative_score_rank = EXCLUDED.fruits_country_alternative_score_rank,
    mania_country_alternative_score_rank = EXCLUDED.mania_country_alternative_score_rank,
    total_country_alternative_score_rank = EXCLUDED.total_country_alternative_score_rank,

    osu_global_replays_watched_rank = EXCLUDED.osu_global_replays_watched_rank,
    taiko_global_replays_watched_rank = EXCLUDED.taiko_global_replays_watched_rank,
    fruits_global_replays_watched_rank = EXCLUDED.fruits_global_replays_watched_rank,
    mania_global_replays_watched_rank = EXCLUDED.mania_global_replays_watched_rank,
    total_global_replays_watched_rank = EXCLUDED.total_global_replays_watched_rank,
    osu_country_replays_watched_rank = EXCLUDED.osu_country_replays_watched_rank,
    taiko_country_replays_watched_rank = EXCLUDED.taiko_country_replays_watched_rank,
    fruits_country_replays_watched_rank = EXCLUDED.fruits_country_replays_watched_rank,
    mania_country_replays_watched_rank = EXCLUDED.mania_country_replays_watched_rank,
    total_country_replays_watched_rank = EXCLUDED.total_country_replays_watched_rank,

    total_global_medals_rank = EXCLUDED.total_global_medals_rank,
    total_country_medals_rank = EXCLUDED.total_country_medals_rank,
    total_global_badges_rank = EXCLUDED.total_global_badges_rank,
    total_country_badges_rank = EXCLUDED.total_country_badges_rank,

    osu_global_playcount_rank = EXCLUDED.osu_global_playcount_rank,
    taiko_global_playcount_rank = EXCLUDED.taiko_global_playcount_rank,
    fruits_global_playcount_rank = EXCLUDED.fruits_global_playcount_rank,
    mania_global_playcount_rank = EXCLUDED.mania_global_playcount_rank,
    total_global_playcount_rank = EXCLUDED.total_global_playcount_rank,
    osu_country_playcount_rank = EXCLUDED.osu_country_playcount_rank,
    taiko_country_playcount_rank = EXCLUDED.taiko_country_playcount_rank,
    fruits_country_playcount_rank = EXCLUDED.fruits_country_playcount_rank,
    mania_country_playcount_rank = EXCLUDED.mania_country_playcount_rank,
    total_country_playcount_rank = EXCLUDED.total_country_playcount_rank,

    osu_global_playtime_rank = EXCLUDED.osu_global_playtime_rank,
    taiko_global_playtime_rank = EXCLUDED.taiko_global_playtime_rank,
    fruits_global_playtime_rank = EXCLUDED.fruits_global_playtime_rank,
    mania_global_playtime_rank = EXCLUDED.mania_global_playtime_rank,
    total_global_playtime_rank = EXCLUDED.total_global_playtime_rank,
    osu_country_playtime_rank = EXCLUDED.osu_country_playtime_rank,
    taiko_country_playtime_rank = EXCLUDED.taiko_country_playtime_rank,
    fruits_country_playtime_rank = EXCLUDED.fruits_country_playtime_rank,
    mania_country_playtime_rank = EXCLUDED.mania_country_playtime_rank,
    total_country_playtime_rank = EXCLUDED.total_country_playtime_rank;
END;
$$;
