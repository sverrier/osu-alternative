CREATE TABLE IF NOT EXISTS logger (
    logType TEXT,
    user_id INTEGER,
    beatmap_id INTEGER,
    CONSTRAINT logger_pkey PRIMARY KEY (logtype,user_id)
)