-- Function: revert_highest_score_osu
CREATE OR REPLACE FUNCTION delete_score_osu()
RETURNS TRIGGER AS $$
DECLARE
    top_score_id BIGINT;
    top_pp_id BIGINT;
BEGIN
    ------------------------------------------------------------------------
    -- Step 1: Revert beatmap stats (SS and FC counts)
    ------------------------------------------------------------------------
    --Ignore difficulty reducing mods
    IF NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(OLD.mods) AS elem
        WHERE elem->>'acronym' IN ('EZ','HT','DC','NR','AT','CN','RX','AP','TP','DA','WU','WD')
    )
    THEN
        -- Revert SS count
        IF OLD.accuracy = 1.0 THEN
            UPDATE beatmapLive
            SET ss_count = GREATEST(ss_count - 1, 0)
            WHERE beatmap_id = OLD.beatmap_id;
        END IF;

        -- Revert FC count
        IF (
            COALESCE(OLD.statistics_miss, 0) = 0
            AND EXISTS (
                SELECT 1
                FROM beatmapLive b
                WHERE b.beatmap_id = OLD.beatmap_id
                  AND COALESCE(OLD.statistics_ok, 0) >= (b.max_combo - OLD.max_combo)
            )
        ) THEN
            UPDATE beatmapLive
            SET fc_count = GREATEST(fc_count - 1, 0)
            WHERE beatmap_id = OLD.beatmap_id;
        END IF;
    END IF;

    ------------------------------------------------------------------------
    -- Step 2: Delete corresponding record from scoreLive
    ------------------------------------------------------------------------
    DELETE FROM scoreLive
    WHERE id = OLD.id;

    ------------------------------------------------------------------------
    -- Step 3: Recompute top score / top pp IDs for this user + beatmap
    ------------------------------------------------------------------------
    SELECT id INTO top_score_id
    FROM scoreOsu
    WHERE beatmap_id = OLD.beatmap_id
      AND user_id = OLD.user_id
    ORDER BY classic_total_score DESC, id ASC
    LIMIT 1;

    SELECT id INTO top_pp_id
    FROM scoreOsu
    WHERE beatmap_id = OLD.beatmap_id
      AND user_id = OLD.user_id
    ORDER BY pp DESC, id ASC
    LIMIT 1;

    ------------------------------------------------------------------------
    -- Step 4: Update highest_score / highest_pp flags
    ------------------------------------------------------------------------
    UPDATE scoreOsu
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = OLD.beatmap_id
      AND user_id = OLD.user_id;

    UPDATE scoreLive
    SET highest_score = (id = top_score_id),
        highest_pp    = (id = top_pp_id)
    WHERE beatmap_id = OLD.beatmap_id
      AND user_id = OLD.user_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger: fire after actual deletes from scoreOsu
DROP TRIGGER IF EXISTS delete_score_osu_trigger ON scoreOsu;

CREATE TRIGGER delete_score_osu_trigger
AFTER DELETE ON scoreOsu
FOR EACH ROW
EXECUTE FUNCTION delete_score_osu();
