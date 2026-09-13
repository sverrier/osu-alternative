CREATE TABLE IF NOT EXISTS registrations (
    user_id INT PRIMARY KEY,
    discordname TEXT,
    discordid TEXT,
    registrationdate TIMESTAMP WITH TIME ZONE,
    is_synced BOOL DEFAULT false
);