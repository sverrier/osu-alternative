insert into beatmaphistory (
 	beatmapset_id,
	difficulty_rating,
	id,
	record_date,
	mode_int,
	passcount,
	playcount,
	beatmapset_play_count,
	beatmapset_ratings
)
select
	bl.beatmapset_id,
	bl.stars,
	bl.beatmap_id ,
	CURRENT_DATE,
	bl."mode" ,
	bl.pass_count ,
	bl.play_count ,
	b.beatmapset_play_count,
	b.beatmapset_ratings
from
	beatmaplive bl
inner join beatmap b on
	bl.beatmap_id = b.id
on
	conflict do nothing;