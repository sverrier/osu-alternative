import json
from .jsonDataObject import jsonDataObject


class Beatmap(jsonDataObject):
    table = "beatmap"  # Hardcoded table name
    key_columns = "id"
    flatten_columns = {"beatmapset_hype"}
    json_columns = {"beatmapset_covers", 
                    "beatmapset_nominations_summary",
                    "beatmapset_availability", 
                    "beatmapset_ratings", 
                    "failtimes", 
                    "owners"}
    column_list = ["beatmapset_id", "difficulty_rating", "id", "mode", "status", "total_length", "user_id", "version", "accuracy", "ar", "bpm", "convert", "count_circles", "count_sliders", "count_spinners", "cs", "current_user_playcount", "deleted_at", "drain", "hit_length", "is_scoreable", "last_updated", "mode_int", "passcount", "playcount", "ranked", "url", "checksum", "max_combo", "beatmapset_artist", "beatmapset_artist_unicode", "beatmapset_creator", "beatmapset_favourite_count", "beatmapset_hype_current", "beatmapset_hype_required", "beatmapset_nsfw", "beatmapset_offset", "beatmapset_play_count", "beatmapset_preview_url", "beatmapset_rating", "beatmapset_source", "beatmapset_spotlight", "beatmapset_status", "beatmapset_title", "beatmapset_title_unicode", "beatmapset_track_id", "beatmapset_genre_id", "beatmapset_language_id", "beatmapset_user_id", "beatmapset_video", "beatmapset_bpm", "beatmapset_can_be_hyped", "beatmapset_deleted_at", "beatmapset_discussion_enabled", "beatmapset_discussion_locked", "beatmapset_is_scoreable", "beatmapset_last_updated", "beatmapset_legacy_thread_url", "beatmapset_ranked", "beatmapset_ranked_date", "beatmapset_storyboard", "beatmapset_submitted_date", "beatmapset_tags", "failtimes", "beatmapset_availability", "owners", "beatmapset_nominations_summary", "beatmapset_covers", "beatmapset_ratings", "beatmapset_anime_cover"]

    def __init__(self, beatmap):
        beatmapset = beatmap.pop("beatmapset", {})
        if isinstance(beatmapset, dict):
            for key, value in beatmapset.items():
                beatmap[f"beatmapset_{key}"] = value
        
        super().__init__(beatmap, self.table, self.key_columns, self.flatten_columns,
                         self.json_columns, self.column_list)
