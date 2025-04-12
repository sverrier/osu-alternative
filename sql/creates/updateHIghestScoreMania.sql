CREATE OR REPLACE FUNCTION update_highest_score_mania() RETURNS TRIGGER AS $$
BEGIN
    -- Step 1: Check if there is an existing highest score for this (beatmap_id, user_id)
    UPDATE scoreMania
    SET highest_score = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND highest_score = TRUE  -- ✅ Only reset the current highest
      AND classic_total_score < NEW.classic_total_score;  -- ✅ Only if the new score is higher

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