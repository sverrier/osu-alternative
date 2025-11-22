CREATE OR REPLACE FUNCTION format_time_from_seconds(total_seconds BIGINT)
RETURNS TEXT AS $$
DECLARE
    h BIGINT;
    m BIGINT;
    s BIGINT;
    result TEXT := '';
BEGIN
    h := total_seconds / 3600;
    m := (total_seconds % 3600) / 60;
    s := total_seconds % 60;

    IF h > 0 THEN
        result := result || h::text || 'h';
    END IF;

    IF m > 0 THEN
        result := result || m::text || 'm';
    END IF;

    -- always include seconds
    result := result || s::text || 's';

    RETURN trim(result);
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;