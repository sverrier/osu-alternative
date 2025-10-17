CREATE OR REPLACE FUNCTION update_highest_score_fruits() RETURNS TRIGGER AS $$
BEGIN
    -- Step 1: Check if there is an existing highest score for this (beatmap_id, user_id)
    UPDATE scoreFruits
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

    UPDATE scoreFruits
    SET highest_pp = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND highest_pp = TRUE  -- ✅ Only reset the current highest
      AND pp < NEW.pp;  -- ✅ Only if the new score is higher

    UPDATE scoreLive
    SET highest_pp = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND highest_pp = TRUE  -- ✅ Only reset the current highest
      AND pp < NEW.pp;

    --Update beatmap statistics on INSERT
    IF TG_OP = 'INSERT' THEN
      IF NEW.accuracy = 1.0 THEN
          UPDATE beatmapLive
          SET ss_count = ss_count + 1
          WHERE beatmap_id = NEW.beatmap_id;
      END IF;

      IF COALESCE(NEW.statistics_miss, 0) = 0 THEN
          UPDATE beatmapLive
          SET fc_count = fc_count + 1
          WHERE beatmap_id = NEW.beatmap_id;
      END IF;
    END IF;

    -- Step 2: Set the new row as the highest score **only if it’s the new best**
    IF NOT EXISTS (
        SELECT 1 FROM scoreFruits 
        WHERE beatmap_id = NEW.beatmap_id 
          AND user_id = NEW.user_id 
          AND highest_score = TRUE
    ) THEN
        UPDATE scoreFruits
        SET highest_score = TRUE
        WHERE id = NEW.id;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM scoreFruits 
        WHERE beatmap_id = NEW.beatmap_id 
          AND user_id = NEW.user_id 
          AND highest_pp = TRUE
    ) THEN
        UPDATE scoreFruits
        SET highest_pp = TRUE
        WHERE id = NEW.id;
    END IF;

    -- Step 3: Insert into scoreLive if user exists
    INSERT INTO scoreLive (
        id, beatmap_id, user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_great,
        maximum_statistics_ignore_hit, maximum_statistics_ignore_miss,
        maximum_statistics_large_bonus, maximum_statistics_large_tick_hit,
        maximum_statistics_small_tick_hit, mods, passed, pp, preserve, processed,
        grade, ranked, replay, ruleset_id, started_at, statistics_great,
        statistics_miss, statistics_ignore_hit, statistics_ignore_miss,
        statistics_large_bonus, statistics_large_tick_hit, statistics_large_tick_miss,
        statistics_small_tick_hit, statistics_small_tick_miss, total_score,
        total_score_without_mods, type, maximum_statistics_legacy_combo_increase,
        maximum_statistics_miss, highest_score, highest_pp, rank
    )
    SELECT
        s.id, s.beatmap_id, s.user_id, s.accuracy, s.best_id, s.build_id, s.classic_total_score,
        s.ended_at, s.has_replay, s.is_perfect_combo, s.legacy_perfect, s.legacy_score_id,
        s.legacy_total_score, s.max_combo, s.maximum_statistics_great,
        s.maximum_statistics_ignore_hit, s.maximum_statistics_ignore_miss,
        s.maximum_statistics_large_bonus, s.maximum_statistics_large_tick_hit,
        s.maximum_statistics_small_tick_hit, s.mods, s.passed, s.pp, s.preserve, s.processed,
        s.rank, s.ranked, s.replay, s.ruleset_id, s.started_at, s.statistics_great,
        s.statistics_miss, s.statistics_ignore_hit, s.statistics_ignore_miss,
        s.statistics_large_bonus, s.statistics_large_tick_hit, s.statistics_large_tick_miss,
        s.statistics_small_tick_hit, s.statistics_small_tick_miss, s.total_score,
        s.total_score_without_mods, s.type, s.maximum_statistics_legacy_combo_increase,
        s.maximum_statistics_miss, s.highest_score, s.highest_pp, s.leaderboard_rank
    FROM scoreFruits s
    WHERE s.id = NEW.id
      AND EXISTS (SELECT 1 FROM userLive WHERE user_id = s.user_id)
    ON CONFLICT DO NOTHING;

    RETURN NULL;  -- ✅ AFTER triggers must return NULL
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS  set_highest_score_fruits on scoreFruits;

-- ✅ Convert to AFTER trigger to avoid conflicts
CREATE TRIGGER set_highest_score_fruits
AFTER INSERT OR UPDATE ON scoreFruits
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL)
EXECUTE FUNCTION update_highest_score_fruits();