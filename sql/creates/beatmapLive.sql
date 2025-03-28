CREATE TABLE IF NOT EXISTS beatmapLive (
    beatmap_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    beatmapset_id INTEGER,
    mode INTEGER,
    status TEXT,
    stars NUMERIC,
    od INTEGER,
    ar NUMERIC,
    bpm NUMERIC,
    cs NUMERIC,
    hp NUMERIC,
    length INTEGER,
    drain_time INTEGER,
    count_circles INTEGER,
    count_sliders INTEGER,
    count_spinners INTEGER,
    max_combo INTEGER,
    pass_count INTEGER,
    play_count INTEGER,
    fc_count INTEGER,
    ss_count INTEGER,
    favourite_count INTEGER,
    ranked_date TIMESTAMP WITH TIME ZONE,
    submitted_date TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE,
    version TEXT,
    title TEXT,
    artist TEXT,
    source TEXT,
    tags TEXT,
    checksum TEXT
);