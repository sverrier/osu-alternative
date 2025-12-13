CREATE OR REPLACE FUNCTION sync_beatmaplive()
RETURNS TRIGGER AS $$
BEGIN
    -- Only sync ranked/approved/loved maps with ranked date
    IF NEW.beatmapset_ranked_date IS NOT NULL
       AND NEW.status IN ('approved', 'loved', 'ranked') THEN

        INSERT INTO public.beatmaplive (
            beatmap_id,
            user_id,
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
            user_id        = EXCLUDED.user_id,
            beatmapset_id  = EXCLUDED.beatmapset_id,
            "mode"         = EXCLUDED."mode",
            status         = EXCLUDED.status,
            stars          = EXCLUDED.stars,
            od             = EXCLUDED.od,
            ar             = EXCLUDED.ar,
            bpm            = EXCLUDED.bpm,
            cs             = EXCLUDED.cs,
            hp             = EXCLUDED.hp,
            length         = EXCLUDED.length,
            drain_time     = EXCLUDED.drain_time,
            count_circles  = EXCLUDED.count_circles,
            count_sliders  = EXCLUDED.count_sliders,
            count_spinners = EXCLUDED.count_spinners,
            max_combo      = EXCLUDED.max_combo,
            pass_count     = EXCLUDED.pass_count,
            play_count     = EXCLUDED.play_count,
            favourite_count = EXCLUDED.favourite_count,
            ranked_date     = EXCLUDED.ranked_date,
            submitted_date  = EXCLUDED.submitted_date,
            last_updated    = EXCLUDED.last_updated,
            "version"       = EXCLUDED."version",
            title           = EXCLUDED.title,
            artist          = EXCLUDED.artist,
            "source"        = EXCLUDED."source",
            tags            = EXCLUDED.tags,
            checksum        = EXCLUDED.checksum,
            track_id        = EXCLUDED.track_id,
            mapper        = EXCLUDED.mapper,
            genre        = EXCLUDED.genre,
            language        = EXCLUDED.language,
            is_spotlight        = EXCLUDED.is_spotlight,
            is_nsfw        = EXCLUDED.is_nsfw,
            rating        = EXCLUDED.rating,
            download_disabled        = EXCLUDED.download_disabled,
            has_video        = EXCLUDED.has_video,
            has_storyboard        = EXCLUDED.has_storyboard,
            beatmap_offset        = EXCLUDED.beatmap_offset;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_beatmaplive ON beatmap;

CREATE TRIGGER trg_sync_beatmaplive
AFTER INSERT OR UPDATE
ON beatmap
FOR EACH ROW
EXECUTE FUNCTION sync_beatmaplive();
