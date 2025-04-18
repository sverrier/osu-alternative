CREATE TABLE IF NOT EXISTS scoreFruits (
    accuracy NUMERIC NOT NULL,
    beatmap_id INTEGER NOT NULL,
    best_id INTEGER NULL,
    build_id INTEGER NULL,
    classic_total_score BIGINT NOT NULL,
    current_user_attributes JSONB NOT NULL,
    ended_at TIMESTAMPTZ NOT NULL,
    has_replay BOOLEAN NOT NULL,
    id BIGINT PRIMARY KEY,
    is_perfect_combo BOOLEAN NOT NULL,
    legacy_perfect BOOLEAN NOT NULL,
    legacy_score_id BIGINT NULL,
    legacy_total_score BIGINT NOT NULL,
    max_combo INTEGER NOT NULL,
    maximum_statistics_great INTEGER NULL,
    maximum_statistics_miss INTEGER NULL,
    maximum_statistics_ignore_hit INTEGER NULL,
    maximum_statistics_ignore_miss INTEGER NULL,
    maximum_statistics_large_bonus INTEGER NULL,
    maximum_statistics_large_tick_hit INTEGER NULL,
    maximum_statistics_small_tick_hit INTEGER NULL,
    maximum_statistics_legacy_combo_increase INTEGER NULL,
    mods JSONB NOT NULL,
    passed BOOLEAN NOT NULL,
    pp NUMERIC NULL,
    preserve BOOLEAN NOT NULL,
    processed BOOLEAN NOT NULL,
    rank VARCHAR(5) NOT NULL,
    ranked BOOLEAN NOT NULL,
    replay BOOLEAN NOT NULL,
    ruleset_id INTEGER NOT NULL,
    started_at TIMESTAMPTZ NULL,
    statistics_great INTEGER NULL,
    statistics_miss INTEGER NULL,
    statistics_ignore_hit INTEGER NULL,
    statistics_ignore_miss INTEGER NULL,
    statistics_large_bonus INTEGER NULL,
    statistics_large_tick_hit INTEGER NULL,
    statistics_large_tick_miss INTEGER NULL,
    statistics_small_tick_hit INTEGER NULL,
    statistics_small_tick_miss INTEGER NULL,
    total_score BIGINT NOT NULL,
    total_score_without_mods BIGINT NULL,
    type VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    highest_score BOOL NULL,
    highest_pp BOOL NULL
);

CREATE INDEX if not exists idx_scoreFruits_ended_at ON scoreFruits USING BRIN (ended_at);

CREATE INDEX IF NOT EXISTS scoreFruits_score 
on scoreFruits(beatmap_id, user_id, classic_total_score desc);

CREATE INDEX IF NOT EXISTS scoreFruits_user
on scoreFruits(user_id);

CREATE INDEX IF NOT EXISTS scoreFruits_beatmap
on scoreFruits(beatmap_id);

CREATE INDEX IF NOT EXISTS idx_scoreFruits_highest_only 
ON scoreFruits (beatmap_id, user_id) 
WHERE highest_score = TRUE;