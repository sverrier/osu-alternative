CREATE TABLE IF NOT EXISTS beatmapHistory (
    beatmapset_id INTEGER,
    difficulty_rating NUMERIC,
    id INTEGER,
    mode_int INTEGER,
    passcount INTEGER,
    playcount INTEGER,
    beatmapset_play_count INTEGER,
    beatmapset_ratings JSONB
);