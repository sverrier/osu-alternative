DELETE FROM beatmaplive bl
WHERE NOT EXISTS (
    SELECT 1 FROM beatmap b
    WHERE b.id = bl.beatmap_id
      AND b.beatmapset_ranked_date IS NOT NULL
      AND b.status IN ('approved','loved','ranked')
);