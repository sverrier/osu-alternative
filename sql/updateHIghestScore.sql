CREATE OR REPLACE FUNCTION update_highest_score() RETURNS TRIGGER AS $$
BEGIN
    -- Reset previous highest score for the same (beatmap_id, user_id)
    UPDATE scoreOsu
    SET highest_score = FALSE
    WHERE beatmap_id = NEW.beatmap_id
      AND user_id = NEW.user_id
      AND classic_total_score < NEW.classic_total_score;
    
    -- Set the new highest score
    NEW.highest_score = TRUE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_highest_score
BEFORE INSERT OR UPDATE ON scoreOsu
FOR EACH ROW
WHEN (NEW.classic_total_score IS NOT NULL)
EXECUTE FUNCTION update_highest_score();
