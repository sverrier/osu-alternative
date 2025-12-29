CREATE OR REPLACE FUNCTION update_highest_score_osu()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
<<calc>>
DECLARE
    top_score_id      BIGINT;
    top_pp_id         BIGINT;

    bm_mode           INT;
    bm_max_combo      INT;

    mod_acronyms      TEXT[];
    mod_speed_change  NUMERIC;

    has_diff_reducing BOOLEAN;
    has_diff_removing BOOLEAN;

    is_same_mode       BOOLEAN;
    allowed_for_counts BOOLEAN;
    is_ss_calc         BOOLEAN;
    is_fc_calc         BOOLEAN;
BEGIN
    SELECT bl.mode, bl.max_combo
      INTO bm_mode, bm_max_combo
    FROM beatmapLive bl
    WHERE bl.beatmap_id = NEW.beatmap_id;

    SELECT array_agg(elem->>'acronym')
      INTO mod_acronyms
    FROM jsonb_array_elements(COALESCE(NEW.mods,'[]'::jsonb)) elem;

    has_diff_reducing := EXISTS (
        SELECT 1
        FROM jsonb_array_elements(COALESCE(NEW.mods,'[]'::jsonb)) elem
        WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
    );

    has_diff_removing := EXISTS (
        SELECT 1
        FROM jsonb_array_elements(COALESCE(NEW.mods,'[]'::jsonb)) elem
        WHERE elem->>'acronym' IN ('NF','AT','CN','RX','AP')
    );

    SELECT COALESCE(
               (
                   SELECT (elem->'settings'->>'speed_change')::numeric
                   FROM jsonb_array_elements(COALESCE(NEW.mods,'[]'::jsonb)) elem
                   WHERE elem->>'acronym' IN ('DT','NC','HT','DC')
                     AND elem->'settings' ? 'speed_change'
                   LIMIT 1
               ),
               (
                   SELECT CASE
                              WHEN elem->>'acronym' IN ('DT','NC') THEN 1.5
                              WHEN elem->>'acronym' IN ('HT','DC') THEN 0.75
                          END
                   FROM jsonb_array_elements(COALESCE(NEW.mods,'[]'::jsonb)) elem
                   WHERE elem->>'acronym' IN ('DT','NC','HT','DC')
                   LIMIT 1
               ),
               1
           )
      INTO mod_speed_change;

    is_same_mode       := (NEW.ruleset_id = bm_mode);
    allowed_for_counts := NOT has_diff_reducing;

    is_ss_calc := (NEW.rank IN ('X','XH'));

    is_fc_calc := CASE
                    WHEN NEW.build_id IS NOT NULL THEN
                      (COALESCE(NEW.statistics_miss,0) = 0
                       AND COALESCE(NEW.statistics_large_tick_miss,0) = 0)
                    ELSE
                      (COALESCE(NEW.statistics_miss,0) = 0
                       AND COALESCE(NEW.statistics_ok,0) >= (COALESCE(bm_max_combo,0) - COALESCE(NEW.max_combo,0)))
                  END;

    -- Beatmap counters maintained regardless of registration status (as before)
    IF is_same_mode AND allowed_for_counts AND is_ss_calc THEN
        UPDATE beatmapLive
           SET ss_count = ss_count + 1
         WHERE beatmap_id = NEW.beatmap_id;
    END IF;

    IF is_same_mode AND allowed_for_counts AND is_fc_calc THEN
        UPDATE beatmapLive
           SET fc_count = fc_count + 1
         WHERE beatmap_id = NEW.beatmap_id;
    END IF;

    -- Only maintain scoreLive for registered users
    IF NOT EXISTS (SELECT 1 FROM userLive WHERE user_id = NEW.user_id) THEN
        RETURN NULL;
    END IF;

    INSERT INTO scoreLive (
        id,
        beatmap_id_fk,
        user_id_fk,
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
        combo,
        maximum_statistics_perfect,
        maximum_statistics_great,
        maximum_statistics_miss,
        maximum_statistics_ignore_hit,
        maximum_statistics_ignore_miss,
        maximum_statistics_slider_tail_hit,
        maximum_statistics_legacy_combo_increase,
        maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit,
        maximum_statistics_small_bonus,
        maximum_statistics_small_tick_hit,
        mods,
        passed,
        pp,
        preserve,
        processed,
        grade,
        ranked,
        replay,
        ruleset_id,
        started_at,
        statistics_perfect,
        statistics_great,
        statistics_good,
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
        statistics_small_tick_hit,
        statistics_small_tick_miss,
        statistics_combo_break,
        total_score,
        total_score_without_mods,
        type,
        highest_score,
        highest_pp,
        rank,
        mod_acronyms,
        mod_speed_change,
        difficulty_reducing,
        difficulty_removing,
        is_ss,
        is_fc,
        attr_diff,
        attr_date,
        attr_recalc
    )
    SELECT
        NEW.id,
        NEW.beatmap_id,
        NEW.user_id,
        NEW.accuracy,
        NEW.best_id,
        NEW.build_id,
        NEW.classic_total_score,
        NEW.ended_at,
        NEW.has_replay,
        NEW.is_perfect_combo,
        NEW.legacy_perfect,
        NEW.legacy_score_id,
        NEW.legacy_total_score,
        NEW.max_combo,
        NULL,
        NEW.maximum_statistics_great,
        NULL,
        NEW.maximum_statistics_ignore_hit,
        NULL,
        NEW.maximum_statistics_slider_tail_hit,
        NEW.maximum_statistics_legacy_combo_increase,
        NEW.maximum_statistics_large_bonus,
        NEW.maximum_statistics_large_tick_hit,
        NEW.maximum_statistics_small_bonus,
        NEW.maximum_statistics_small_tick_hit,
        NEW.mods,
        NEW.passed,
        NEW.pp,
        NEW.preserve,
        NEW.processed,
        NEW.rank,
        NEW.ranked,
        NEW.replay,
        NEW.ruleset_id,
        NEW.started_at,
        NULL,
        NEW.statistics_great,
        NULL,
        NEW.statistics_ok,
        NEW.statistics_meh,
        NEW.statistics_miss,
        NEW.statistics_ignore_hit,
        NEW.statistics_ignore_miss,
        NEW.statistics_slider_tail_hit,
        NEW.statistics_slider_tail_miss,
        NEW.statistics_large_bonus,
        NEW.statistics_large_tick_hit,
        NEW.statistics_large_tick_miss,
        NEW.statistics_small_bonus,
        NEW.statistics_small_tick_hit,
        NEW.statistics_small_tick_miss,
        NULL,
        NEW.total_score,
        NEW.total_score_without_mods,
        NEW.type,
        FALSE,
        FALSE,
        NEW.leaderboard_rank,
        COALESCE(calc.mod_acronyms, ARRAY[]::text[]),
        COALESCE(calc.mod_speed_change, 1),
        has_diff_reducing,
        has_diff_removing,
        is_ss_calc,
        is_fc_calc,
        NULL,
        NULL,
        NULL
    ON CONFLICT (id) DO NOTHING;

    -- Highest flags computed only from scoreLive
    SELECT id
      INTO top_score_id
    FROM scoreLive
    WHERE beatmap_id_fk = NEW.beatmap_id
      AND user_id_fk    = NEW.user_id
    ORDER BY
      (ruleset_id = bm_mode) DESC NULLS LAST,
      classic_total_score DESC NULLS LAST,
      id ASC
    LIMIT 1;

    SELECT id
      INTO top_pp_id
    FROM scoreLive
    WHERE beatmap_id_fk = NEW.beatmap_id
      AND user_id_fk    = NEW.user_id
    ORDER BY
      (ruleset_id = bm_mode) DESC NULLS LAST,
      pp DESC NULLS LAST,
      id ASC
    LIMIT 1;

    WITH desired AS (
      SELECT sl.id,
             (sl.id = top_score_id) AS new_highest_score,
             (sl.id = top_pp_id)    AS new_highest_pp
      FROM scoreLive sl
      WHERE sl.beatmap_id_fk = NEW.beatmap_id
        AND sl.user_id_fk    = NEW.user_id
    )
    UPDATE scoreLive sl
       SET highest_score = d.new_highest_score,
           highest_pp    = d.new_highest_pp
      FROM desired d
     WHERE sl.id = d.id
       AND (sl.highest_score IS DISTINCT FROM d.new_highest_score
            OR sl.highest_pp IS DISTINCT FROM d.new_highest_pp);

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS set_highest_score_osu ON scoreOsu;
CREATE TRIGGER set_highest_score_osu
AFTER INSERT ON scoreOsu
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL OR NEW.pp IS NOT NULL)
EXECUTE FUNCTION update_highest_score_osu();
