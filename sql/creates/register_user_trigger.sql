-- 1) Trigger function
CREATE OR REPLACE FUNCTION register_user_from_registrations()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM public.userLive u
        WHERE u.user_id = NEW.user_id
    ) THEN
        CALL register_user(NEW.user_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- 2) Trigger on registrations
DROP TRIGGER IF EXISTS trg_register_user_on_insert ON public.registrations;

CREATE TRIGGER trg_register_user_on_insert
AFTER INSERT
ON public.registrations
FOR EACH ROW
EXECUTE FUNCTION register_user_from_registrations();