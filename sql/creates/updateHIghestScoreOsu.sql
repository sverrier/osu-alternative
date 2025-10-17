CREATE OR REPLACE FUNCTION update_highest_score_osu()
RETURNS TRIGGER AS $$
DECLARE
    top_score_id BIGINT;
    top_pp_id BIGINT;
BEGIN

    ------------------------------------------------------------------------
    -- Step 1: Update beatmap stats
    ------------------------------------------------------------------------
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

    ------------------------------------------------------------------------
    -- Step 2: Compute top score and pp IDs into variables
    ------------------------------------------------------------------------
    SELECT id INTO top_score_id
    FROM scoreOsu
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
    ORDER BY classic_total_score DESC, id ASC
    LIMIT 1;

    SELECT id INTO top_pp_id
    FROM scoreOsu
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
    ORDER BY pp DESC, id ASC
    LIMIT 1;

    ------------------------------------------------------------------------
    -- Step 3: Update flags in both scoreOsu and scoreLive
    ------------------------------------------------------------------------
    UPDATE scoreOsu
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id;

    UPDATE scoreLive
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id;

    ------------------------------------------------------------------------
    -- Step 4: Sync into scoreLive (insert or update)
    ------------------------------------------------------------------------
    INSERT INTO scoreLive (
        id, beatmap_id, user_id, accuracy, best_id, build_id, classic_total_score,
        ended_at, has_replay, is_perfect_combo, legacy_perfect, legacy_score_id,
        legacy_total_score, max_combo, maximum_statistics_great,
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
        highest_pp, rank
    )
    SELECT
        s.id, s.beatmap_id, s.user_id, s.accuracy, s.best_id, s.build_id, s.classic_total_score,
        s.ended_at, s.has_replay, s.is_perfect_combo, s.legacy_perfect, s.legacy_score_id,
        s.legacy_total_score, s.max_combo, s.maximum_statistics_great,
        s.maximum_statistics_ignore_hit, s.maximum_statistics_slider_tail_hit,
        s.maximum_statistics_legacy_combo_increase, s.maximum_statistics_large_bonus,
        s.maximum_statistics_large_tick_hit, s.maximum_statistics_small_bonus, s.mods,
        s.passed, s.pp, s.preserve, s.processed, s.rank, s.ranked, s.replay, s.ruleset_id,
        s.started_at, s.statistics_great, s.statistics_ok, s.statistics_meh,
        s.statistics_miss, s.statistics_ignore_hit, s.statistics_ignore_miss,
        s.statistics_slider_tail_hit, s.statistics_slider_tail_miss,
        s.statistics_large_bonus, s.statistics_large_tick_hit,
        s.statistics_large_tick_miss, s.statistics_small_bonus, s.total_score,
        s.total_score_without_mods, s.type, s.statistics_small_tick_hit,
        s.statistics_small_tick_miss, s.maximum_statistics_small_tick_hit, s.highest_score,
        s.highest_pp, s.leaderboard_rank
    FROM scoreOsu s
    WHERE s.id = NEW.id
      AND EXISTS (SELECT 1 FROM userLive WHERE user_id = s.user_id)
    ON CONFLICT (id) DO NOTHING;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_highest_score_osu ON scoreOsu;

CREATE TRIGGER set_highest_score_osu
AFTER INSERT ON scoreOsu
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL OR NEW.pp IS NOT NULL)
EXECUTE FUNCTION update_highest_score_osu();
