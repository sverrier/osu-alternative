TableColumns = {
    "beatmapLive": ["beatmap_id","beatmapset_id","mode","status","stars","od","ar","bpm","cs","hp","length","drain_time","count_circles","count_sliders","count_spinners","max_combo","pass_count","play_count","fc_count","ss_count","favourite_count","ranked_date","submitted_date","last_updated","version","title","artist","source","tags","checksum"],
    "scoreLive": ["id","accuracy","best_id","build_id","classic_total_score","ended_at","has_replay","is_perfect_combo","legacy_perfect","legacy_score_id","legacy_total_score","max_combo","maximum_statistics_perfect","maximum_statistics_great","maximum_statistics_miss","maximum_statistics_ignore_hit","maximum_statistics_ignore_miss","maximum_statistics_slider_tail_hit","maximum_statistics_legacy_combo_increase","maximum_statistics_large_bonus","maximum_statistics_large_tick_hit","maximum_statistics_small_bonus","maximum_statistics_small_tick_hit","mods","passed","pp","preserve","processed","grade","ranked","replay","ruleset_id","started_at","statistics_perfect","statistics_great","statistics_good","statistics_ok","statistics_meh","statistics_miss","statistics_ignore_hit","statistics_ignore_miss","statistics_slider_tail_hit","statistics_slider_tail_miss","statistics_large_bonus","statistics_large_tick_hit","statistics_large_tick_miss","statistics_small_bonus","statistics_small_tick_hit","statistics_small_tick_miss","statistics_combo_break","total_score","total_score_without_mods","type","highest_score","highest_pp"],
    "userLive": ["user_id","username","country_code","country_name","osu_count_100","osu_count_300","osu_count_50","osu_count_miss","osu_global_rank","osu_grade_counts_a","osu_grade_counts_s","osu_grade_counts_sh","osu_grade_counts_ss","osu_grade_counts_ssh","osu_hit_accuracy","osu_level_current","osu_level_progress","osu_maximum_combo","osu_play_count","osu_play_time","osu_pp","osu_ranked_score","osu_replays_watched_by_others","osu_total_hits","osu_total_score","taiko_count_100","taiko_count_300","taiko_count_50","taiko_count_miss","taiko_global_rank","taiko_grade_counts_a","taiko_grade_counts_s","taiko_grade_counts_sh","taiko_grade_counts_ss","taiko_grade_counts_ssh","taiko_hit_accuracy","taiko_level_current","taiko_level_progress","taiko_maximum_combo","taiko_play_count","taiko_play_time","taiko_pp","taiko_ranked_score","taiko_replays_watched_by_others","taiko_total_hits","taiko_total_score","fruits_count_100","fruits_count_300","fruits_count_50","fruits_count_miss","fruits_global_rank","fruits_grade_counts_a","fruits_grade_counts_s","fruits_grade_counts_sh","fruits_grade_counts_ss","fruits_grade_counts_ssh","fruits_hit_accuracy","fruits_level_current","fruits_level_progress","fruits_maximum_combo","fruits_play_count","fruits_play_time","fruits_pp","fruits_ranked_score","fruits_replays_watched_by_others","fruits_total_hits","fruits_total_score","mania_count_100","mania_count_300","mania_count_50","mania_count_miss","mania_global_rank","mania_grade_counts_a","mania_grade_counts_s","mania_grade_counts_sh","mania_grade_counts_ss","mania_grade_counts_ssh","mania_hit_accuracy","mania_level_current","mania_level_progress","mania_maximum_combo","mania_play_count","mania_play_time","mania_pp","mania_ranked_score","mania_replays_watched_by_others","mania_total_hits","mania_total_score","team_flag_url","team_id","team_name","team_short_name"]
}

JoinClauses = {
    "scoreLive,beatmapLive": " inner join beatmapLive on scoreLive.beatmap_id = beatmapLive.beatmap_id",
    "beatmapLive,scoreLive": " inner join scoreLive on beatmapLive.beatmap_id = scoreLive.beatmap_id",
    "scoreLive,userLive": " inner join userLive on scoreLive.user_id = userLive.user_id",
    "userLive,scoreLive": " inner join scoreLive on userLive.user_id = scoreLive.user_id",
}

class QueryBuilder:
    def __init__(self, args, columns=None, table=None, group=None, limit=None):
        self.args = args
        self.fields = []
        self.setSelectClause(columns)
        self.setWhereClause()
        self.setFromClause(table)
        self.setGroupByClause(group)
        self.setLimitClause(limit)

    
    def setSelectClause(self, columns):
        for column in columns.split(", "):
            self.fields.append(column)
        self.selectclause = "SELECT " + columns
        print(self.selectclause)

    def setFromClause(self, table):
        # Identify tables involved
        tables = set()
        if table is not None:
            tables.add(table)
        for field in self.fields:
            for table, columns in TableColumns.items():
                if field in columns:
                    tables.add(table)

        # Order tables, prioritize "score" if present
        table_order = sorted(tables)
        if "scoreLive" in table_order:
            table_order.remove("scoreLive")
            table_order.insert(0, "scoreLive")

        # Construct FROM clause
        self.fromclause = f" FROM {table_order[0]}"
        joined_tables = {table_order[0]}  # Track already joined tables

        # Process remaining tables
        for i in range(1, len(table_order)):
            current_table = table_order[i]
            found_join = False

            for prev_table in joined_tables:  # Find first valid join
                key = f"{prev_table},{current_table}"
                if key in JoinClauses:
                    self.fromclause += JoinClauses[key]
                    joined_tables.add(current_table)
                    found_join = True
                    break  # Stop once we find the first valid join
            
            if not found_join:
                raise ValueError(f"Missing join condition for {current_table}")


    def setWhereClause(self):
        whereClause = ""
        for key, value in self.args.items():
            if key == "-accuracy-min":
                whereClause += " AND accuracy >= " + value
                self.fields.append("accuracy")
            elif key == "-accuracy-max":
                whereClause += " AND accuracy < " + value
                self.fields.append("accuracy")
            elif key == "-mode":
                whereClause += " AND mode = " + value
                self.fields.append("mode") 
            elif key == "-username":
                whereClause += " AND UPPER(username) = UPPER('" + value + "')"
                self.fields.append("username")
            elif key == "-unplayed":
                whereClause += " AND beatmapLive.beatmap_id not in (select beatmap_id from scoreLive where user_id = " + value + ")"
                self.fields.append("beatmap_id")
            elif key == "-grade":
                whereClause += " AND grade = upper('" + value + "')"
                self.fields.append("grade")
            elif key == "-highest_score":
                whereClause += " AND highest_score = " + value
                self.fields.append("highest_score")
            elif key == "-highest_pp":
                whereClause += " AND highest_pp = " + value
                self.fields.append("highest_pp")
            elif key == "-date_played-min":
                whereClause += " AND cast(ended_at as date) >= '" + value + "'"
                self.fields.append("ended_at")
            elif key == "-date_played-max":
                whereClause += " AND cast(ended_at as date) < '" + value + "'"
                self.fields.append("ended_at")
            elif key == "-tags":
                whereClause += " AND concat(artist, ',', title, ',', source, ',', version, ',', tags) LIKE '" + value + "'"
                self.fields.append("artist")
                self.fields.append("title")
                self.fields.append("source")
                self.fields.append("version")
                self.fields.append("tags")
            else: #Attempt to generically resolve parameter
                all_columns = set(col for cols in TableColumns.values() for col in cols)
                raw_key = key[1:]
                
                if raw_key.endswith("-min"):
                    column = raw_key[:-4]
                    if column in all_columns:
                        whereClause += f" AND {column} >= {value}"
                        self.fields.append(column)
                elif raw_key.endswith("-max"):
                    column = raw_key[:-4]
                    if column in all_columns:
                        whereClause += f" AND {column} < {value}"
                        self.fields.append(column)
                elif raw_key in all_columns:
                    whereClause += f" AND {raw_key} = {value}"
                    self.fields.append(raw_key)

        if len(whereClause) > 0:
            self.whereclause = " WHERE " + whereClause[5:]
        else:
            self.whereclause = ""
    
    def setGroupByClause(self, group):
        self.groupbyclause = ""
        if group is not None:
            self.groupbyclause = group 

        for key, value in self.args.items():
            if key == "-aggregate":
                self.groupbyclause = value
        
        if self.groupbyclause != "":
            self.groupbyclause = " GROUP BY " + self.groupbyclause

    def setLimitClause(self, limit):
        self.limitclause = ""
        if limit is not None:
            self.limitclause = limit 

        for key, value in self.args.items():
            if key == "-limit":
                self.limitclause = value
        
        if self.limitclause != "":
            self.limitclause = " LIMIT " + self.limitclause

    def getQuery(self):
        print(self.selectclause + self.fromclause + self.whereclause + self.groupbyclause + self.limitclause)
        return self.selectclause + self.fromclause + self.whereclause + self.groupbyclause + self.limitclause
        

