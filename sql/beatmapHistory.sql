CREATE TABLE IF NOT EXISTS beatmapHistory (
    id INTEGER,
    record_date DATE,
    beatmapset_id INTEGER,
    difficulty_rating NUMERIC,
    mode_int INTEGER,
    passcount INTEGER,
    playcount INTEGER,
    beatmapset_play_count INTEGER,
    beatmapset_ratings JSONB,
    PRIMARY KEY (id, record_date)
);