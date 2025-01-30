import json

class Beatmap:
    TABLE_NAME = "beatmaps"  # Hardcoded table name
    JSONB_COLUMNS = {"covers", "nominations_summary", "availability", "failtimes", "owners"}

    def __init__(self, beatmap):
        self.beatmap = beatmap

    def __str__(self):
        return json.dumps(self.beatmap, indent=4)

    def escape_sql_string(self, value):
        """
        Escape single quotes in SQL strings by replacing ' with ''.
        Also wraps the value in single quotes.
        """
        if value is None:
            return "NULL"  # Handle NULL values properly
        return "'" + value.replace("'", "''") + "'"  # Correctly escape single quotes

    def generate_insert_query(self):
        """
        Generate an INSERT SQL query for the PostgreSQL 'beatmaps' table.
        Properly escapes strings and stores specific fields as JSONB.
        """

        # Define columns that should be flattened from 'beatmapset'
        beatmapset_columns = {
            "artist", "artist_unicode", "creator", "favourite_count", "id", "nsfw", "offset",
            "play_count", "preview_url", "source", "spotlight", "status", "title",
            "title_unicode", "user_id", "video", "bpm", "can_be_hyped", "deleted_at",
            "discussion_enabled", "discussion_locked", "is_scoreable", "last_updated",
            "legacy_thread_url", "ranked", "ranked_date", "storyboard", "submitted_date", 
            "tags"
        }

        # Flatten 'beatmapset' fields
        beatmapset_data = self.beatmap.pop("beatmapset", {})
        flattened_data = {f"beatmapset_{k}": v for k, v in beatmapset_data.items() if k in beatmapset_columns}

        # Extract JSONB fields
        jsonb_data = {key: self.beatmap.pop(key, {}) for key in self.JSONB_COLUMNS}

        # Merge all data together
        final_data = {**self.beatmap, **flattened_data, **jsonb_data}

        # Prepare column names and values
        columns = ', '.join(f'"{col}"' for col in final_data.keys())
        values = ', '.join(
            f"'{json.dumps(value)}'::jsonb" if col in self.JSONB_COLUMNS else
            self.escape_sql_string(value) if isinstance(value, str) else
            ('TRUE' if value is True else 'FALSE' if value is False else 'NULL' if value is None else str(value))
            for col, value in final_data.items()
        )

        # Generate SQL query
        query = f"INSERT INTO BEATMAP ({columns}) VALUES ({values});"
        return query