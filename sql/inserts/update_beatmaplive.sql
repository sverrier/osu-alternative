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
    checksum
)
SELECT
    b.id,
    b.user_id,
    b.beatmapset_id,
    b.mode_int,
    b.status,
    b.difficulty_rating,
    b.accuracy,
    b.ar,
    b.bpm,
    b.cs,
    b.drain,
    b.total_length,
    b.hit_length,
    b.count_circles,
    b.count_sliders,
    b.count_spinners,
    b.max_combo,
    b.passcount,
    b.playcount,
    0,  -- fc_count
    0,  -- ss_count
    b.beatmapset_favourite_count,
    b.beatmapset_ranked_date,
    b.beatmapset_submitted_date,
    b.beatmapset_last_updated,
    b."version",
    b.beatmapset_title,
    b.beatmapset_artist,
    b.beatmapset_source,
    b.beatmapset_tags,
    b.checksum
FROM beatmap b
WHERE b.beatmapset_ranked_date IS NOT NULL
  AND b.status IN ('approved', 'loved', 'ranked')

ON CONFLICT (beatmap_id)
DO UPDATE SET
    user_id = EXCLUDED.user_id,
    beatmapset_id = EXCLUDED.beatmapset_id,
    "mode" = EXCLUDED."mode",
    status = EXCLUDED.status,
    stars = EXCLUDED.stars,
    od = EXCLUDED.od,
    ar = EXCLUDED.ar,
    bpm = EXCLUDED.bpm,
    cs = EXCLUDED.cs,
    hp = EXCLUDED.hp,
    length = EXCLUDED.length,
    drain_time = EXCLUDED.drain_time,
    count_circles = EXCLUDED.count_circles,
    count_sliders = EXCLUDED.count_sliders,
    count_spinners = EXCLUDED.count_spinners,
    max_combo = EXCLUDED.max_combo,
    pass_count = EXCLUDED.pass_count,
    play_count = EXCLUDED.play_count,
    favourite_count = EXCLUDED.favourite_count,
    ranked_date = EXCLUDED.ranked_date,
    submitted_date = EXCLUDED.submitted_date,
    last_updated = EXCLUDED.last_updated,
    "version" = EXCLUDED."version",
    title = EXCLUDED.title,
    artist = EXCLUDED.artist,
    "source" = EXCLUDED."source",
    tags = EXCLUDED.tags,
    checksum = EXCLUDED.checksum;

DELETE FROM beatmaplive bl
WHERE NOT EXISTS (
    SELECT 1 FROM beatmap b
    WHERE b.id = bl.beatmap_id
      AND b.beatmapset_ranked_date IS NOT NULL
      AND b.status IN ('approved','loved','ranked')
);