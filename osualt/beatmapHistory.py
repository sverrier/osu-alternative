import json
from osualt.jsonDataObject import jsonDataObject
from datetime import datetime



class BeatmapHistory(jsonDataObject):
    table = "beatmapHistory"  # Hardcoded table name
    flatten_columns = {"beatmapset_hype"}
    json_columns = {"beatmapset_covers", 
                    "beatmapset_nominations_summary",
                    "beatmapset_availability", 
                    "beatmapset_ratings", 
                    "failtimes", 
                    "owners"}

    included_columns = {'beatmapset_id', 'difficulty_rating', 'id', 'record_date', 'mode_int', 'passcount', 'playcount', 'beatmapset_play_count', 'beatmapset_ratings'}

    def __init__(self, beatmap):
        for key, value in beatmap.pop("beatmapset", {}).items():
            beatmap[f"beatmapset_{key}"] = value

        beatmap["record_date"] = datetime.today().strftime('%Y-%m-%d')
        
        super().__init__(beatmap, self.table, self.flatten_columns,
                         self.json_columns)
                         
    def generate_insert_query(self):
        self.final_json = {key: value for key, value in self.final_json.items() if key in self.included_columns}
        return super().generate_insert_query()
