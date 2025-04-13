CREATE OR REPLACE FUNCTION update_highest_score_mania() RETURNS TRIGGER AS $$
BEGIN
    -- Step 1: Check if there is an existing highest score for this (beatmap_id, user_id)
    UPDATE scoreMania
    SET highest_score = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND highest_score = TRUE  -- ✅ Only reset the current highest
      AND classic_total_score < NEW.classic_total_score;  -- ✅ Only if the new score is higher

    UPDATE scoreLive
    SET highest_score = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND highest_score = TRUE  -- ✅ Only reset the current highest
      AND classic_total_score < NEW.classic_total_score;

    -- Step 2: Set the new row as the highest score **only if it’s the new best**
    IF NOT EXISTS (
        SELECT 1 FROM scoreMania 
        WHERE beatmap_id = NEW.beatmap_id 
          AND user_id = NEW.user_id 
          AND highest_score = TRUE
    ) THEN
        UPDATE scoreMania
        SET highest_score = TRUE
        WHERE id = NEW.id;
    END IF;

    -- Step 3: Insert into scoreLive if user exists
    INSERT INTO scoreLive (
        id, beatmap_id, user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_legacy_combo_increase,
        maximum_statistics_perfect, maximum_statistics_ignore_hit, mods, passed, pp,
        preserve, processed, grade, ranked, replay, ruleset_id, started_at,
        statistics_combo_break, statistics_perfect, statistics_great, statistics_good,
        statistics_ok, statistics_meh, statistics_miss, statistics_ignore_hit,
        statistics_ignore_miss, total_score, total_score_without_mods, type,
        highest_score, highest_pp
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
        NEW.highest_score, NEW.highest_pp
    WHERE EXISTS (
        SELECT 1 FROM userLive WHERE user_id = NEW.user_id
    )
    ON CONFLICT DO NOTHING;



    RETURN NULL;  -- ✅ AFTER triggers must return NULL
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS  set_highest_score_mania on scoreMania;

-- ✅ Convert to AFTER trigger to avoid conflicts
CREATE TRIGGER set_highest_score_mania
AFTER INSERT OR UPDATE ON scoreMania
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL)
EXECUTE FUNCTION update_highest_score_mania();