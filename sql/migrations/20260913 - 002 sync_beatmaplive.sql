-- DROP FUNCTION public.sync_beatmaplive();

CREATE OR REPLACE FUNCTION public.sync_beatmaplive()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    is_new_beatmapset BOOLEAN;
BEGIN

    -- Only sync ranked/approved/loved maps with ranked date
    IF NEW.beatmapset_ranked_date IS NOT NULL
       AND NEW.status IN ('approved', 'loved', 'ranked') THEN

        /*
         * Determine whether this beatmapset is genuinely new to beatmaplive.
         *
         * This is checked BEFORE inserting the beatmap, so if this is the
         * first ranked/approved/loved beatmap from the set, we can generate
         * the new_beatmapset event.
         */
        SELECT NOT EXISTS (
            SELECT 1
            FROM public.beatmaplive
            WHERE beatmapset_id = NEW.beatmapset_id
        )
        INTO is_new_beatmapset;


        INSERT INTO public.beatmaplive (
            beatmap_id,
            mapper_id,
            beatmapset_id,
            "mode",
            status,
            stars,
            od,
            ar,
            bpm,
            cs,
            hp,
            length,
            drain_time,
            count_circles,
            count_sliders,
            count_spinners,
            max_combo,
            pass_count,
            play_count,
            fc_count,
            ss_count,
            favourite_count,
            ranked_date,
            submitted_date,
            last_updated,
            "version",
            title,
            artist,
            "source",
            tags,
            checksum,
            track_id,
            mapper,
            genre,
            language,
            is_spotlight,
            is_nsfw,
            rating,
            download_disabled,
            has_video,
            has_storyboard,
            beatmap_offset
        )
        VALUES (
            NEW.id,
            NEW.user_id,
            NEW.beatmapset_id,
            NEW.mode_int,
            NEW.status,
            NEW.difficulty_rating,
            NEW.accuracy,
            NEW.ar,
            NEW.bpm,
            NEW.cs,
            NEW.drain,
            NEW.total_length,
            NEW.hit_length,
            NEW.count_circles,
            NEW.count_sliders,
            NEW.count_spinners,
            NEW.max_combo,
            NEW.passcount,
            NEW.playcount,
            0, -- fc_count
            0, -- ss_count
            NEW.beatmapset_favourite_count,
            NEW.beatmapset_ranked_date,
            NEW.beatmapset_submitted_date,
            NEW.beatmapset_last_updated,
            NEW."version",
            NEW.beatmapset_title,
            NEW.beatmapset_artist,
            NEW.beatmapset_source,
            NEW.beatmapset_tags,
            NEW.checksum,
            NEW.beatmapset_track_id,
            NEW.beatmapset_creator,
            NEW.beatmapset_genre_id,
            NEW.beatmapset_language_id,
            NEW.beatmapset_spotlight,
            NEW.beatmapset_nsfw,
            NEW.beatmapset_rating,
            (NEW.beatmapset_availability::jsonb ->> 'download_disabled')::boolean,
            NEW.beatmapset_storyboard,
            NEW.beatmapset_video,
            NEW.beatmapset_offset
        )
        ON CONFLICT (beatmap_id)
        DO UPDATE SET
            mapper_id            = EXCLUDED.mapper_id,
            beatmapset_id        = EXCLUDED.beatmapset_id,
            "mode"               = EXCLUDED."mode",
            status               = EXCLUDED.status,
            stars                = EXCLUDED.stars,
            od                   = EXCLUDED.od,
            ar                   = EXCLUDED.ar,
            bpm                  = EXCLUDED.bpm,
            cs                   = EXCLUDED.cs,
            hp                   = EXCLUDED.hp,
            length               = EXCLUDED.length,
            drain_time           = EXCLUDED.drain_time,
            count_circles        = EXCLUDED.count_circles,
            count_sliders        = EXCLUDED.count_sliders,
            count_spinners       = EXCLUDED.count_spinners,
            max_combo            = EXCLUDED.max_combo,
            pass_count           = EXCLUDED.pass_count,
            play_count           = EXCLUDED.play_count,
            favourite_count     = EXCLUDED.favourite_count,
            ranked_date          = EXCLUDED.ranked_date,
            submitted_date      = EXCLUDED.submitted_date,
            last_updated        = EXCLUDED.last_updated,
            "version"           = EXCLUDED."version",
            title               = EXCLUDED.title,
            artist              = EXCLUDED.artist,
            "source"            = EXCLUDED."source",
            tags                = EXCLUDED.tags,
            checksum            = EXCLUDED.checksum,
            track_id            = EXCLUDED.track_id,
            mapper              = EXCLUDED.mapper,
            genre               = EXCLUDED.genre,
            language            = EXCLUDED.language,
            is_spotlight        = EXCLUDED.is_spotlight,
            is_nsfw             = EXCLUDED.is_nsfw,
            rating              = EXCLUDED.rating,
            download_disabled   = EXCLUDED.download_disabled,
            has_video           = EXCLUDED.has_video,
            has_storyboard      = EXCLUDED.has_storyboard,
            beatmap_offset      = EXCLUDED.beatmap_offset;


        /*
         * If this was the first beatmap from the set to enter beatmaplive,
         * generate the new beatmapset event.
         */
        IF is_new_beatmapset THEN
            INSERT INTO events (
                event_type,
                beatmap_id
            )
            VALUES (
                'new_beatmapset',
                NEW.beatmapset_id
            );
        END IF;

    END IF;

    RETURN NEW;

END;
$function$
;

-- Permissions

ALTER FUNCTION public.sync_beatmaplive() OWNER TO postgres;
GRANT ALL ON FUNCTION public.sync_beatmaplive() TO public;
GRANT ALL ON FUNCTION public.sync_beatmaplive() TO postgres;
