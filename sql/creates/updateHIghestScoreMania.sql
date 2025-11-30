CREATE OR REPLACE FUNCTION update_highest_score_mania() RETURNS TRIGGER AS $$
DECLARE
    top_score_id BIGINT;
    top_pp_id BIGINT;
BEGIN
    ------------------------------------------------------------------------
    -- Step 1: Update beatmap stats
    ------------------------------------------------------------------------
    IF NEW.ruleset_id = (
        SELECT mode
        FROM beatmapLive
        WHERE beatmap_id = NEW.beatmap_id
    )
    THEN
        IF NOT EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.mods) AS elem
            WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
        )
        THEN
            IF NEW.rank = 'X' or NEW.rank = 'XH' THEN
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
                    AND (2 *(COALESCE(NEW.statistics_good, 0) + COALESCE(NEW.statistics_ok, 0))) >= (b.max_combo - NEW.max_combo)
                )
            ) THEN
                UPDATE beatmapLive
                SET fc_count = fc_count + 1
                WHERE beatmap_id = NEW.beatmap_id;
            END IF;
        END IF;
    END IF;

    ------------------------------------------------------------------------
    -- Step 2: Compute top score and pp IDs into variables
    ------------------------------------------------------------------------
    SELECT id INTO top_score_id
    FROM scoreMania
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
    ORDER BY classic_total_score DESC, id ASC
    LIMIT 1;

    SELECT id INTO top_pp_id
    FROM scoreMania
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
    ORDER BY pp DESC, id ASC
    LIMIT 1;

    ------------------------------------------------------------------------
    -- Step 3: Sync into scoreLive (insert or update)
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id, user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, combo, maximum_statistics_legacy_combo_increase,
        maximum_statistics_perfect, maximum_statistics_ignore_hit, mods, passed, pp,
        preserve, processed, grade, ranked, replay, ruleset_id, started_at,
        statistics_combo_break, statistics_perfect, statistics_great, statistics_good,
        statistics_ok, statistics_meh, statistics_miss, statistics_ignore_hit,
        statistics_ignore_miss, total_score, total_score_without_mods, type,
        highest_score, highest_pp, rank, mod_acronyms, mod_speed_change, difficulty_reducing, difficulty_removing
    )
    SELECT
        NEW.id, NEW.beatmap_id, NEW.user_id, NEW.accuracy, NEW.best_id, NEW.build_id, NEW.classic_total_score,
        NEW.ended_at, NEW.has_replay, NEW.is_perfect_combo, NEW.legacy_perfect, NEW.legacy_score_id,
        NEW.legacy_total_score, NEW.max_combo, NEW.maximum_statistics_legacy_combo_increase,
        NEW.maximum_statistics_perfect, NEW.maximum_statistics_ignore_hit, NEW.mods, NEW.passed, NEW.pp,
        NEW.preserve, NEW.processed, NEW.rank, NEW.ranked, NEW.replay, NEW.ruleset_id, NEW.started_at,
        NEW.statistics_combo_break, NEW.statistics_perfect, NEW.statistics_great, NEW.statistics_good,
        NEW.statistics_ok, NEW.statistics_meh, NEW.statistics_miss, NEW.statistics_ignore_hit,
        NEW.statistics_ignore_miss, NEW.total_score, NEW.total_score_without_mods, NEW.type,
        NEW.highest_score, NEW.highest_pp, NEW.leaderboard_rank,
        (
            SELECT array_agg(elem->>'acronym')
            FROM jsonb_array_elements(NEW.mods) elem
        ) as mod_acronyms,
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
        ) as mod_speed_change,
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.mods) elem
            WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
        ) as difficulty_reducing,
        EXISTS (
            SELECT 1
            FROM jsonb_array_elements(NEW.mods) elem
            WHERE elem->>'acronym' IN ('NF','AT','CN','RX','AP')
        ) as difficulty_removing
    FROM (SELECT 1) as dummy_select
    WHERE EXISTS (SELECT 1 FROM userLive WHERE user_id = NEW.user_id)
    ON CONFLICT (id) DO NOTHING;

    ------------------------------------------------------------------------
    -- Step 4: Update flags in both scoreOsu and scoreLive
    ------------------------------------------------------------------------
    UPDATE scoreMania
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id;

    UPDATE scoreLive
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id;



    RETURN NULL;  -- ✅ AFTER triggers must return NULL
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS  set_highest_score_mania on scoreMania;

-- ✅ Convert to AFTER trigger to avoid conflicts
CREATE TRIGGER set_highest_score_mania
AFTER INSERT ON scoreMania
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL)
EXECUTE FUNCTION update_highest_score_mania();