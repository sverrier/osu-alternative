CREATE TABLE if not EXISTS scoreTaiko (
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
    maximum_statistics_great INTEGER NOT NULL,
    maximum_statistics_large_bonus INTEGER NULL,
    maximum_statistics_small_bonus INTEGER NULL,
    maximum_statistics_ignore_hit INTEGER NULL,
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
    statistics_ok INTEGER NULL,
    statistics_miss INTEGER NULL,
    statistics_large_bonus INTEGER NULL,
    statistics_ignore_hit INTEGER NULL,
    statistics_ignore_miss INTEGER NULL,
    statistics_small_bonus INTEGER NULL,
    total_score BIGINT NOT NULL,
    total_score_without_mods BIGINT NULL,
    type VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    highest_score BOOL NULL,
    highest_pp BOOL NULL
);

CREATE INDEX if not exists idx_scoreTaiko_ended_at ON scoreTaiko USING BRIN (ended_at);

CREATE INDEX IF NOT EXISTS scoreTaiko_score 
on scoreTaiko(beatmap_id, user_id, classic_total_score desc);

CREATE INDEX IF NOT EXISTS scoreTaiko_user
on scoreTaiko(user_id);

CREATE INDEX IF NOT EXISTS scoreTaiko_beatmap
on scoreTaiko(beatmap_id);

CREATE INDEX IF NOT EXISTS idx_scoreTaiko_highest_only 
ON scoreTaiko (beatmap_id, user_id) 
WHERE highest_score = TRUE;