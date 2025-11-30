-- db/migrations/update_highest_score_osu.sql
CREATE OR REPLACE FUNCTION update_highest_score_osu()
RETURNS TRIGGER AS $$
DECLARE
    top_score_id BIGINT;
    top_pp_id BIGINT;
    bm_mode INT; -- from beatmapLive (mode)
BEGIN
    ------------------------------------------------------------------------
    -- Load beatmap mode
    ------------------------------------------------------------------------
    SELECT bl.mode
    INTO bm_mode
    FROM beatmapLive bl
    WHERE bl.beatmap_id = NEW.beatmap_id;

    ------------------------------------------------------------------------
    -- Step 1: Update beatmap stats unless play is on a convert
    ------------------------------------------------------------------------
    IF NEW.ruleset_id = bm_mode THEN
        IF NOT EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.mods) AS elem
            WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
        ) THEN
            IF NEW.accuracy = 1.0 THEN
                UPDATE beatmapLive
                SET ss_count = ss_count + 1
                WHERE beatmap_id = NEW.beatmap_id;
            END IF;

            IF (
                COALESCE(NEW.statistics_miss, 0) = 0
                AND EXISTS (
                    SELECT 1
                    FROM beatmapLive b
                    WHERE b.beatmap_id = NEW.beatmap_id
                      AND COALESCE(NEW.statistics_ok, 0) >= (b.max_combo - NEW.max_combo)
                )
            ) THEN
                UPDATE beatmapLive
                SET fc_count = fc_count + 1
                WHERE beatmap_id = NEW.beatmap_id;
            END IF;
        END IF;
    END IF;

    ------------------------------------------------------------------------
    -- Step 2: Compute top score/pp IDs, prioritizing ruleset_id = bm_mode
    ------------------------------------------------------------------------
    SELECT id
    INTO top_score_id
    FROM scoreOsu
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id    = NEW.user_id
    ORDER BY
      (ruleset_id = bm_mode) DESC NULLS LAST,
      classic_total_score DESC NULLS LAST,
      id ASC
    LIMIT 1;

    SELECT id
    INTO top_pp_id
    FROM scoreOsu
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id    = NEW.user_id
    ORDER BY
      (ruleset_id = bm_mode) DESC NULLS LAST,
      pp DESC NULLS LAST,
      id ASC
    LIMIT 1;

    ------------------------------------------------------------------------
    -- Step 3: Sync into scoreLive if user is registered
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id, user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_great,
        maximum_statistics_ignore_hit, maximum_statistics_slider_tail_hit,
        maximum_statistics_legacy_combo_increase, maximum_statistics_large_bonus,
        maximum_statistics_large_tick_hit, maximum_statistics_small_bonus, mods,
        passed, pp, preserve, processed, grade, ranked, replay, ruleset_id,
        started_at, statistics_great, statistics_ok, statistics_meh,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_slider_tail_hit, statistics_slider_tail_miss,
        statistics_large_bonus, statistics_large_tick_hit,
        statistics_large_tick_miss, statistics_small_bonus, total_score,
        total_score_without_mods, type, statistics_small_tick_hit,
        statistics_small_tick_miss, maximum_statistics_small_tick_hit, highest_score,
        highest_pp, rank, mod_acronyms, mod_speed_change, difficulty_reducing, difficulty_removing
    )
    SELECT
        NEW.id, NEW.beatmap_id, NEW.user_id, NEW.accuracy, NEW.best_id, NEW.build_id, NEW.classic_total_score,
        NEW.ended_at, NEW.has_replay, NEW.is_perfect_combo, NEW.legacy_perfect, NEW.legacy_score_id,
        NEW.legacy_total_score, NEW.max_combo, NEW.maximum_statistics_great,
        NEW.maximum_statistics_ignore_hit, NEW.maximum_statistics_slider_tail_hit,
        NEW.maximum_statistics_legacy_combo_increase, NEW.maximum_statistics_large_bonus,
        NEW.maximum_statistics_large_tick_hit, NEW.maximum_statistics_small_bonus, NEW.mods,
        NEW.passed, NEW.pp, NEW.preserve, NEW.processed, NEW.rank, NEW.ranked, NEW.replay, NEW.ruleset_id,
        NEW.started_at, NEW.statistics_great, NEW.statistics_ok, NEW.statistics_meh,
        NEW.statistics_miss, NEW.statistics_ignore_hit, NEW.statistics_ignore_miss,
        NEW.statistics_slider_tail_hit, NEW.statistics_slider_tail_miss,
        NEW.statistics_large_bonus, NEW.statistics_large_tick_hit,
        NEW.statistics_large_tick_miss, NEW.statistics_small_bonus, NEW.total_score,
        NEW.total_score_without_mods, NEW.type, NEW.statistics_small_tick_hit,
        NEW.statistics_small_tick_miss, NEW.maximum_statistics_small_tick_hit, NEW.highest_score,
        NEW.highest_pp, NEW.leaderboard_rank,
        (
            SELECT array_agg(elem->>'acronym')
            FROM jsonb_array_elements(NEW.mods) elem
        ) AS mod_acronyms,
        COALESCE(
            (
                SELECT (elem->'settings'->>'speed_change')::numeric
                FROM jsonb_array_elements(NEW.mods) elem
                WHERE elem->>'acronym' IN ('DT','NC','HT','DC')
                  AND elem->'settings' ? 'speed_change'
                LIMIT 1
            ),
            (
                SELECT CASE
                    WHEN elem->>'acronym' IN ('DT','NC') THEN 1.5
                    WHEN elem->>'acronym' IN ('HT','DC') THEN 0.75
                END
                FROM jsonb_array_elements(NEW.mods) elem
                WHERE elem->>'acronym' IN ('DT','NC','HT','DC')
                LIMIT 1
            )
        ) AS mod_speed_change,
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.mods) elem
            WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
        ) AS difficulty_reducing,
        EXISTS (
            SELECT 1 
            FROM jsonb_array_elements(NEW.mods) elem
            WHERE elem->>'acronym' IN ('NF','AT','CN','RX','AP')
        ) AS difficulty_removing
    FROM (SELECT 1) AS dummy_select
    WHERE EXISTS (SELECT 1 FROM userLive WHERE user_id = NEW.user_id)
    ON CONFLICT (id) DO NOTHING;

    ------------------------------------------------------------------------
    -- Step 4: Update flags in both scoreOsu and scoreLive
    ------------------------------------------------------------------------
    UPDATE scoreOsu
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id    = NEW.user_id;

    UPDATE scoreLive
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id    = NEW.user_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_highest_score_osu ON scoreOsu;

CREATE TRIGGER set_highest_score_osu
AFTER INSERT ON scoreOsu
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL OR NEW.pp IS NOT NULL)
EXECUTE FUNCTION update_highest_score_osu();
