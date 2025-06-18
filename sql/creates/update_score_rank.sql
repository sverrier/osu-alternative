CREATE OR REPLACE FUNCTION update_score_rank() RETURNS TRIGGER AS $$
BEGIN
    -- Re-rank all highest_score=TRUE scores for this beatmap
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY beatmap_id
                   ORDER BY classic_total_score DESC
               ) AS new_rank
        FROM scoreOsu
        WHERE highest_score = TRUE
          AND beatmap_id = NEW.beatmap_id
    )
    UPDATE scoreOsu s
    SET leaderboard_rank = r.new_rank
    FROM ranked r
    WHERE s.id = r.id;

    UPDATE scoreLive s
    SET rank = r.new_rank
    FROM ranked r
    WHERE s.id = r.id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
