CREATE TABLE IF NOT EXISTS public.beatmapPack (
    tag                 text PRIMARY KEY,
    name                text NOT NULL,
    author              text NOT NULL,
    pack_date           timestamptz NOT NULL,
    url                 text NOT NULL,
    no_diff_reduction   boolean NOT NULL DEFAULT false,
    ruleset_id          integer NULL,
    beatmapset_ids      integer[] NOT NULL
);