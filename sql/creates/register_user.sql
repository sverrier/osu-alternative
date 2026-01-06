CREATE OR REPLACE PROCEDURE register_user(p_user_id bigint)
LANGUAGE plpgsql
AS $$
BEGIN
	------------------------------------------------------------------------
    -- Step 1: Register user from userMaster into userLive
    ------------------------------------------------------------------------
	UPDATE userMaster set is_registered = true where id = p_user_id;

    INSERT INTO public.userlive (
        user_id, username, country_code, country_name,
        osu_count_100, osu_count_300, osu_count_50, osu_count_miss,
        osu_global_rank, osu_grade_counts_a, osu_grade_counts_s, osu_grade_counts_sh,
        osu_grade_counts_ss, osu_grade_counts_ssh, osu_hit_accuracy, osu_level_current,
        osu_level_progress, osu_maximum_combo, osu_play_count, osu_play_time, osu_pp,
        osu_ranked_score, osu_replays_watched_by_others, osu_total_hits, osu_total_score,
        taiko_count_100, taiko_count_300, taiko_count_50, taiko_count_miss,
        taiko_global_rank, taiko_grade_counts_a, taiko_grade_counts_s, taiko_grade_counts_sh,
        taiko_grade_counts_ss, taiko_grade_counts_ssh, taiko_hit_accuracy, taiko_level_current,
        taiko_level_progress, taiko_maximum_combo, taiko_play_count, taiko_play_time,
        taiko_pp, taiko_ranked_score, taiko_replays_watched_by_others, taiko_total_hits,
        taiko_total_score, fruits_count_100, fruits_count_300, fruits_count_50, fruits_count_miss,
        fruits_global_rank, fruits_grade_counts_a, fruits_grade_counts_s, fruits_grade_counts_sh,
        fruits_grade_counts_ss, fruits_grade_counts_ssh, fruits_hit_accuracy,
        fruits_level_current, fruits_level_progress, fruits_maximum_combo, fruits_play_count,
        fruits_play_time, fruits_pp, fruits_ranked_score, fruits_replays_watched_by_others,
        fruits_total_hits, fruits_total_score, mania_count_100, mania_count_300, mania_count_50,
        mania_count_miss, mania_global_rank, mania_grade_counts_a, mania_grade_counts_s,
        mania_grade_counts_sh, mania_grade_counts_ss, mania_grade_counts_ssh,
        mania_hit_accuracy, mania_level_current, mania_level_progress, mania_maximum_combo,
        mania_play_count, mania_play_time, mania_pp, mania_ranked_score,
        mania_replays_watched_by_others, mania_total_hits, mania_total_score,
        team_flag_url, team_id, team_name, team_short_name
    )
    SELECT
        id, username, country_code, country_name,
        osu_count_100, osu_count_300, osu_count_50, osu_count_miss,
        osu_global_rank, osu_grade_counts_a, osu_grade_counts_s, osu_grade_counts_sh,
        osu_grade_counts_ss, osu_grade_counts_ssh, osu_hit_accuracy, osu_level_current,
        osu_level_progress, osu_maximum_combo, osu_play_count, osu_play_time, osu_pp,
        osu_ranked_score, osu_replays_watched_by_others, osu_total_hits, osu_total_score,
        taiko_count_100, taiko_count_300, taiko_count_50, taiko_count_miss,
        taiko_global_rank, taiko_grade_counts_a, taiko_grade_counts_s, taiko_grade_counts_sh,
        taiko_grade_counts_ss, taiko_grade_counts_ssh, taiko_hit_accuracy, taiko_level_current,
        taiko_level_progress, taiko_maximum_combo, taiko_play_count, taiko_play_time,
        taiko_pp, taiko_ranked_score, taiko_replays_watched_by_others, taiko_total_hits,
        taiko_total_score, fruits_count_100, fruits_count_300, fruits_count_50, fruits_count_miss,
        fruits_global_rank, fruits_grade_counts_a, fruits_grade_counts_s, fruits_grade_counts_sh,
        fruits_grade_counts_ss, fruits_grade_counts_ssh, fruits_hit_accuracy,
        fruits_level_current, fruits_level_progress, fruits_maximum_combo, fruits_play_count,
        fruits_play_time, fruits_pp, fruits_ranked_score, fruits_replays_watched_by_others,
        fruits_total_hits, fruits_total_score, mania_count_100, mania_count_300, mania_count_50,
        mania_count_miss, mania_global_rank, mania_grade_counts_a, mania_grade_counts_s,
        mania_grade_counts_sh, mania_grade_counts_ss, mania_grade_counts_ssh,
        mania_hit_accuracy, mania_level_current, mania_level_progress, mania_maximum_combo,
        mania_play_count, mania_play_time, mania_pp, mania_ranked_score,
        mania_replays_watched_by_others, mania_total_hits, mania_total_score,
        team_flag_url, team_id, team_name, team_short_name
    FROM userMaster
    WHERE id = p_user_id
    ON CONFLICT (user_id) DO NOTHING;

    ------------------------------------------------------------------------
    -- Step 2: Populate scoreLive entries for this user
    ------------------------------------------------------------------------

    ------------------------------------------------------------------------
    -- osu!standard
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id_fk, user_id_fk, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_great,
        maximum_statistics_ignore_hit, maximum_statistics_slider_tail_hit,
        maximum_statistics_legacy_combo_increase, maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit, maximum_statistics_small_bonus, mods,
        passed, pp, preserve, processed, grade, ranked, replay, ruleset_id,
        started_at, statistics_great, statistics_ok, statistics_meh,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_large_bonus, statistics_large_tick_hit,
        statistics_large_tick_miss, statistics_small_bonus,
        statistics_small_tick_hit, statistics_small_tick_miss, total_score,
        total_score_without_mods, type,
        highest_score, highest_pp, rank, mod_acronyms, mod_speed_change,
        difficulty_reducing, difficulty_removing, is_ss, is_fc
    )
    SELECT
        id, beatmap_id, so.user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_great,
        maximum_statistics_ignore_hit, maximum_statistics_slider_tail_hit,
        maximum_statistics_legacy_combo_increase, maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit, maximum_statistics_small_bonus, mods,
        passed, pp, preserve, processed, rank, ranked, replay, ruleset_id,
        started_at, statistics_great, statistics_ok, statistics_meh,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_large_bonus, statistics_large_tick_hit,
        statistics_large_tick_miss, statistics_small_bonus,
        statistics_small_tick_hit, statistics_small_tick_miss, total_score,
        total_score_without_mods, type,
        FALSE, FALSE, leaderboard_rank,
        NULL::text[], 1::numeric, FALSE, FALSE, FALSE, FALSE
    FROM scoreosu so
    WHERE so.user_id = p_user_id
    ON CONFLICT DO NOTHING;

    ------------------------------------------------------------------------
    -- osu!taiko
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        accuracy, beatmap_id_fk, best_id, build_id, classic_total_score, ended_at,
        has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_great,
        maximum_statistics_large_bonus, maximum_statistics_small_bonus,
        maximum_statistics_ignore_hit, maximum_statistics_legacy_combo_increase, mods, passed, pp, preserve, processed,
        grade, ranked, replay, ruleset_id, started_at, statistics_great,
        statistics_ok, statistics_miss, statistics_large_bonus,
        statistics_ignore_hit, statistics_ignore_miss, statistics_small_bonus,
        total_score, total_score_without_mods, type, user_id_fk,
        maximum_statistics_legacy_combo_increase,
        highest_score, highest_pp, rank, mod_acronyms, mod_speed_change,
        difficulty_reducing, difficulty_removing, is_ss, is_fc
    )
    SELECT
        accuracy, beatmap_id, best_id, build_id, classic_total_score, ended_at,
        has_replay, id, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_great,
        maximum_statistics_large_bonus, maximum_statistics_small_bonus,
        maximum_statistics_ignore_hit, maximum_statistics_legacy_combo_increase, mods, passed, pp, preserve, processed,
        rank, ranked, replay, ruleset_id, started_at, statistics_great,
        statistics_ok, statistics_miss, statistics_large_bonus,
        statistics_ignore_hit, statistics_ignore_miss, statistics_small_bonus,
        total_score, total_score_without_mods, type, so.user_id,
        maximum_statistics_legacy_combo_increase,
        FALSE, FALSE, leaderboard_rank,
        NULL::text[], 1::numeric, FALSE, FALSE, FALSE, FALSE
    FROM scoretaiko so
    WHERE so.user_id = p_user_id
    ON CONFLICT DO NOTHING;

    ------------------------------------------------------------------------
    -- osu!mania
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id_fk, user_id_fk, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_legacy_combo_increase,
        maximum_statistics_perfect, maximum_statistics_ignore_hit, mods,
        passed, pp, preserve, processed, grade, ranked, replay, ruleset_id,
        started_at, statistics_combo_break, statistics_perfect, statistics_great, statistics_good, statistics_ok, statistics_meh,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss, total_score,
        total_score_without_mods, type,
        highest_score, highest_pp, rank, mod_acronyms, mod_speed_change,
        difficulty_reducing, difficulty_removing, is_ss, is_fc
    )
    SELECT
        id, beatmap_id, so.user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_legacy_combo_increase,
        maximum_statistics_perfect, maximum_statistics_ignore_hit, mods,
        passed, pp, preserve, processed, rank, ranked, replay, ruleset_id,
        started_at, statistics_combo_break, statistics_perfect, statistics_great, statistics_good, statistics_ok, statistics_meh,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss, total_score,
        total_score_without_mods, type,
        FALSE, FALSE, leaderboard_rank,
        NULL::text[], 1::numeric, FALSE, FALSE, FALSE, FALSE
    FROM scoremania so
    WHERE so.user_id = p_user_id
    ON CONFLICT DO NOTHING;

    ------------------------------------------------------------------------
    -- osu!catch (fruits)
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id_fk, user_id_fk, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_great, maximum_statistics_miss, maximum_statistics_ignore_hit,
        maximum_statistics_ignore_miss, maximum_statistics_legacy_combo_increase, maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit, maximum_statistics_small_tick_hit, mods,
        passed, pp, preserve, processed, grade, ranked, replay, ruleset_id,
        started_at, statistics_great,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_large_bonus, statistics_large_tick_hit,
        statistics_large_tick_miss,
        statistics_small_tick_hit, statistics_small_tick_miss, total_score,
        total_score_without_mods, type,
        highest_score, highest_pp, rank, mod_acronyms, mod_speed_change,
        difficulty_reducing, difficulty_removing, is_ss, is_fc
    )
    SELECT
        id, beatmap_id, so.user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_great, maximum_statistics_miss, maximum_statistics_ignore_hit,
        maximum_statistics_ignore_miss, maximum_statistics_legacy_combo_increase, maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit, maximum_statistics_small_tick_hit, mods,
        passed, pp, preserve, processed, rank, ranked, replay, ruleset_id,
        started_at, statistics_great,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_large_bonus, statistics_large_tick_hit,
        statistics_large_tick_miss,
        statistics_small_tick_hit, statistics_small_tick_miss, total_score,
        total_score_without_mods, type,
        FALSE, FALSE, leaderboard_rank,
        NULL::text[], 1::numeric, FALSE, FALSE, FALSE, FALSE
    FROM scorefruits so
    WHERE so.user_id = p_user_id
    ON CONFLICT DO NOTHING;

    ------------------------------------------------------------------------
    -- Step 3.1: Recompute derived fields in scoreLive for this user
    ------------------------------------------------------------------------
    UPDATE scoreLive sl
    SET mod_acronyms = x.mod_acronyms,
        mod_speed_change = x.mod_speed_change,
        difficulty_reducing = x.has_diff_reducing,
        difficulty_removing = x.has_diff_removing,
        is_ss = x.is_ss_calc,
        is_fc = x.is_fc_calc
    FROM (
        SELECT
            sl2.id,
            COALESCE(array_agg(e->>'acronym'), ARRAY[]::text[]) AS mod_acronyms,
            COALESCE(
                (
                    SELECT (e2->'settings'->>'speed_change')::numeric
                    FROM jsonb_array_elements(COALESCE(sl2.mods,'[]'::jsonb)) e2
                    WHERE e2->>'acronym' IN ('DT','NC','HT','DC')
                      AND e2->'settings' ? 'speed_change'
                    LIMIT 1
                ),
                (
                    SELECT CASE
                             WHEN e3->>'acronym' IN ('DT','NC') THEN 1.5
                             WHEN e3->>'acronym' IN ('HT','DC') THEN 0.75
                           END
                    FROM jsonb_array_elements(COALESCE(sl2.mods,'[]'::jsonb)) e3
                    WHERE e3->>'acronym' IN ('DT','NC','HT','DC')
                    LIMIT 1
                ),
                1
            ) AS mod_speed_change,
            EXISTS (
                SELECT 1
                FROM jsonb_array_elements(COALESCE(sl2.mods,'[]'::jsonb)) e4
                WHERE e4->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
            ) AS has_diff_reducing,
            EXISTS (
                SELECT 1
                FROM jsonb_array_elements(COALESCE(sl2.mods,'[]'::jsonb)) e5
                WHERE e5->>'acronym' IN ('NF','AT','CN','RX','AP')
            ) AS has_diff_removing,
            (sl2.grade IN ('X','XH')) AS is_ss_calc,
            CASE
              WHEN sl2.build_id IS NOT NULL THEN
                (COALESCE(sl2.statistics_miss,0) = 0 AND COALESCE(sl2.statistics_large_tick_miss,0) = 0)
              ELSE
                (COALESCE(sl2.statistics_miss,0) = 0
                 AND COALESCE(bl.max_combo,0) >= 0
                 AND COALESCE(sl2.statistics_ok,0) >= (COALESCE(bl.max_combo,0) - COALESCE(sl2.combo,0)))
            END AS is_fc_calc
        FROM scoreLive sl2
        JOIN beatmapLive bl ON bl.beatmap_id = sl2.beatmap_id_fk
        LEFT JOIN LATERAL jsonb_array_elements(COALESCE(sl2.mods,'[]'::jsonb)) e ON TRUE
        WHERE sl2.user_id_fk = p_user_id
        GROUP BY
            sl2.id, sl2.mods, sl2.grade, sl2.build_id,
            sl2.statistics_miss, sl2.statistics_large_tick_miss,
            sl2.statistics_ok, bl.max_combo, sl2.combo
    ) x
    WHERE sl.id = x.id;

    ------------------------------------------------------------------------
    -- Step 3.2: Recompute highest_score / highest_pp in scoreLive for this user
    ------------------------------------------------------------------------
    WITH ranked AS (
        SELECT
            sl.id,
            row_number() OVER (
                PARTITION BY sl.user_id_fk, sl.beatmap_id_fk
                ORDER BY
                  (sl.ruleset_id = bl.mode) DESC NULLS LAST,
                  sl.classic_total_score DESC NULLS LAST,
                  sl.id ASC
            ) AS rn_score,
            row_number() OVER (
                PARTITION BY sl.user_id_fk, sl.beatmap_id_fk
                ORDER BY
                  (sl.ruleset_id = bl.mode) DESC NULLS LAST,
                  sl.pp DESC NULLS LAST,
                  sl.id ASC
            ) AS rn_pp
        FROM scoreLive sl
        JOIN beatmapLive bl
          ON bl.beatmap_id = sl.beatmap_id_fk
        WHERE sl.user_id_fk = p_user_id
    )
    UPDATE scoreLive sl
       SET highest_score = (r.rn_score = 1),
           highest_pp    = (r.rn_pp = 1)
      FROM ranked r
     WHERE sl.id = r.id
       AND (
            sl.highest_score IS DISTINCT FROM (r.rn_score = 1)
         OR sl.highest_pp    IS DISTINCT FROM (r.rn_pp = 1)
       );

END;
$$;
