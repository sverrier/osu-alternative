CREATE TABLE IF NOT EXISTS scoreLive (
    id BIGINT PRIMARY KEY,
    beatmap_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    accuracy NUMERIC NOT NULL,
    best_id INTEGER NULL,
    build_id INTEGER NULL,
    classic_total_score BIGINT NOT NULL,
    ended_at TIMESTAMPTZ NOT NULL,
    has_replay BOOLEAN NOT NULL,
    is_perfect_combo BOOLEAN NOT NULL,
    legacy_perfect BOOLEAN NOT NULL,
    legacy_score_id BIGINT NULL,
    legacy_total_score BIGINT NOT NULL,
    max_combo INTEGER NOT NULL,
    maximum_statistics_perfect INTEGER NULL,
    maximum_statistics_great INTEGER NULL,
    maximum_statistics_miss INTEGER NULL,
    maximum_statistics_ignore_hit INTEGER NULL,
    maximum_statistics_ignore_miss INTEGER NULL,
    maximum_statistics_slider_tail_hit INTEGER NULL,
    maximum_statistics_legacy_combo_increase INTEGER NULL,
    maximum_statistics_large_bonus INTEGER NULL,
    maximum_statistics_large_tick_hit INTEGER NULL,
    maximum_statistics_small_bonus INTEGER NULL,
    maximum_statistics_small_tick_hit INTEGER NULL,
    mods JSONB NOT NULL,
    passed BOOLEAN NOT NULL,
    pp NUMERIC NULL,
    preserve BOOLEAN NOT NULL,
    processed BOOLEAN NOT NULL,
    rank VARCHAR(3) NOT NULL,
    ranked BOOLEAN NOT NULL,
    replay BOOLEAN NOT NULL,
    ruleset_id INTEGER NOT NULL,
    started_at TIMESTAMPTZ NULL,
    statistics_perfect INTEGER NULL,
    statistics_great INTEGER NULL,
    statistics_good INTEGER NULL,
    statistics_ok INTEGER NULL,
    statistics_meh INTEGER NULL,
    statistics_miss INTEGER NULL,
    statistics_ignore_hit INTEGER NULL,
    statistics_ignore_miss INTEGER NULL,
    statistics_slider_tail_hit INTEGER NULL,
    statistics_slider_tail_miss INTEGER NULL,
    statistics_large_bonus INTEGER NULL,
    statistics_large_tick_hit INTEGER NULL,
    statistics_large_tick_miss INTEGER NULL,
    statistics_small_bonus INTEGER NULL,
    statistics_small_tick_hit INTEGER NULL,
    statistics_small_tick_miss INTEGER NULL,
    statistics_combo_break INTEGER NULL,
    total_score BIGINT NULL,
    total_score_without_mods BIGINT NULL,
    type VARCHAR(50) NOT NULL,
    highest_score BOOL NULL,
    highest_pp BOOL NULL
);

CREATE INDEX if not exists idx_scoreLive_ended_at ON scoreLive USING BRIN (ended_at);

CREATE INDEX IF NOT EXISTS scoreLive_score 
on scoreLive(beatmap_id, user_id, classic_total_score desc);

CREATE INDEX IF NOT EXISTS scoreLive_user
on scoreLive(user_id);

CREATE INDEX IF NOT EXISTS scoreLive_beatmap
on scoreLive(beatmap_id);

CREATE INDEX IF NOT EXISTS idx_scoreLive_highest_only 
ON scoreLive (beatmap_id, user_id) 
WHERE highest_score = TRUE;