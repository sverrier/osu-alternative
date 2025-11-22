from bot.util.schema import TABLE_METADATA, validate_column, get_all_columns, get_column_info

TableColumns = {
    "beatmapLive": list(TABLE_METADATA["beatmapLive"].keys()),
    "scoreLive": list(TABLE_METADATA["scoreLive"].keys()),
    "userLive": list(TABLE_METADATA["userLive"].keys())
}

JoinClauses = {
    "scoreLive,beatmapLive": " inner join beatmapLive on scoreLive.beatmap_id = beatmapLive.beatmap_id",
    "beatmapLive,scoreLive": " inner join scoreLive on beatmapLive.beatmap_id = scoreLive.beatmap_id",
    "scoreLive,userLive": " inner join userLive on scoreLive.user_id = userLive.user_id",
    "userLive,scoreLive": " inner join scoreLive on userLive.user_id = scoreLive.user_id",
}

# Special cases that don't follow standard patterns
VALUED_PARAMS = {
    "-username": ("UPPER(username) = UPPER({value})", ["username"]),
    "-user_id": ("userLive.user_id = {value}", ["user_id"]),
    "-unplayed": ("NOT EXISTS (SELECT 1 FROM scoreLive WHERE scoreLive.beatmap_id = beatmapLive.beatmap_id and scoreLive.ruleset_id = beatmapLive.mode and user_id = {value})", ["beatmap_id"]),
    "-search": ("LOWER(CONCAT(artist, ',', title, ',', source, ',', version, ',', tags)) LIKE LOWER({value})", ["artist", "title", "source", "version", "tags"]),
    "-is_fa-true": ("track_id IS NOT NULL", ["track_id"]),
    "-is_fa-false": ("track_id IS NULL", ["track_id"]),
    "-year": ("EXTRACT(YEAR FROM ranked_date) = {value}", ["ranked_date"]),
}

VALUELESS_PARAMS = {
    "-is_fa": ("track_id IS NOT NULL", ["track_id"]),
    "-not_fa": ("track_id IS NULL", ["track_id"]),
    "-has_replay": ("has_replay = true", ["has_replay"]),
    "-no_replay": ("has_replay = false", ["has_replay"]),
    "-convertless": ("scoreLive.ruleset_id = beatmapLive.mode", ["mode", "ruleset_id"]),
}

PARAM_SYNONYM_MAP = {
    "-u": "-username",
}

class QueryBuilder:
    def __init__(self, args, columns=None, table=None, group=None, order=None, limit=None):
        self.args = args
        self.fields = []
        self.tables = set()
        self.params = []  # For parameterized queries
        if table is not None:
            self.tables.add(table)
        self.setSelectClause(columns)
        self.setWhereClause()
        self.setFromClause(table)
        self.setGroupByClause(group)
        self.setOrderByClause(order)
        self.setLimitClause(limit)

    def _format_value(self, column, value, operator=None):
        """
        Format value with proper quoting based on column type.
        Returns formatted value string ready for SQL.
        
        Args:
            column: Column name
            value: Raw value
            operator: Optional operator (for special handling like LIKE)
        """
        meta = get_column_info(column)
        if not meta:
            # If no metadata, treat as string to be safe
            return f"'{value}'"
        
        col_type = meta.get("type")
        
        # Handle different types
        if col_type in ("int", "float", "bool"):
            # Numeric types - no quotes
            return str(value)
        elif col_type == "datetime":
            # Dates need quotes
            return f"'{value}'"
        elif col_type == "str":
            # Strings need quotes
            # Special handling for LIKE operator
            if operator == "like":
                return f"'%{value}%'"
            return f"'{value}'"
        elif col_type in ("jsonb", "array"):
            # JSON/array types - no quotes (assume proper formatting)
            return str(value)
        else:
            # Default to quoted
            return f"'{value}'"
    
    def _make_case_insensitive(self, column, formatted_value, operator):
        """
        Wrap column and value in UPPER() for case-insensitive comparison.
        Only applies to string columns.
        
        Args:
            column: Column name
            formatted_value: Already formatted value with quotes
            operator: SQL operator (=, !=, IN, NOT IN, LIKE, etc.)
        
        Returns:
            Tuple of (column_expr, value_expr)
        """
        meta = get_column_info(column)
        if meta and meta.get("type") == "str":
            # Strip quotes, uppercase, re-quote
            if formatted_value.startswith("'") and formatted_value.endswith("'"):
                inner_value = formatted_value[1:-1]
                return f"UPPER({column})", f"UPPER('{inner_value}')"
            return f"UPPER({column})", f"UPPER({formatted_value})"
        return column, formatted_value
    
    def _parse_list_value(self, value):
        """
        Parse comma-separated list into SQL-ready format.
        Returns list of individual values.
        """
        if isinstance(value, str):
            return [v.strip() for v in value.split(',')]
        return [value]
    
    def setSelectClause(self, columns):
        for column in columns.split(", "):
            self.fields.append(column)
        self.selectclause = "SELECT " + columns
        print(self.selectclause)

    def setFromClause(self, table):
        # Identify tables involved
        print(self.fields)
        print(self.tables)
        for field in self.fields:
            for table, columns in TableColumns.items():
                if field in columns:
                    self.tables.add(table)

        print(self.tables)

        # Order tables, prioritize "score" if present
        table_order = sorted(self.tables)
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
        where_clauses = []

        for key, value in self.args.items():
            key = PARAM_SYNONYM_MAP.get(key, key)
            
            # Handle valueless parameters
            if key in VALUELESS_PARAMS:
                clause, deps = VALUELESS_PARAMS[key]
                where_clauses.append(clause)
                self.fields.extend(deps)
                continue

            # Handle special boolean variants
            if key == "-is_fa":
                key = f"-is_fa-{value.lower()}"

            # Check for special cases first
            if key in VALUED_PARAMS:
                template, deps = VALUED_PARAMS[key]
                
                # Format value based on dependencies
                if deps and len(deps) > 0:
                    formatted_value = self._format_value(deps[0], value)
                else:
                    formatted_value = str(value)
                
                # Special handling for -tags (LIKE operator)
                if key == "-tags":
                    formatted_value = f"'%{value}%'"
                
                clause = template.format(value=formatted_value)
                where_clauses.append(clause)
                self.fields.extend(deps)
                continue

            # Parse standardized parameter pattern
            raw_key = key.lstrip("-")
            
            # Check for operators
            if raw_key.endswith("-min"):
                column = raw_key[:-4]
                if validate_column(column):
                    formatted_value = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(column, formatted_value, ">=")
                    where_clauses.append(f"{col_expr} >= {val_expr}")
                    self.fields.append(column)
                    
            elif raw_key.endswith("-max"):
                column = raw_key[:-4]
                if validate_column(column):
                    formatted_value = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(column, formatted_value, "<")
                    where_clauses.append(f"{col_expr} < {val_expr}")
                    self.fields.append(column)
                    
            elif raw_key.endswith("-not"):
                column = raw_key[:-4]
                if validate_column(column):
                    formatted_value = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(column, formatted_value, "!=")
                    where_clauses.append(f"{col_expr} != {val_expr}")
                    self.fields.append(column)
                    
            elif raw_key.endswith("-in"):
                column = raw_key[:-3]
                if validate_column(column):
                    values = self._parse_list_value(value)
                    formatted_values = [self._format_value(column, v) for v in values]
                    # Apply case insensitivity to each value
                    meta = get_column_info(column)
                    if meta and meta.get("type") == "str":
                        col_expr = f"UPPER({column})"
                        upper_values = []
                        for fv in formatted_values:
                            if fv.startswith("'") and fv.endswith("'"):
                                inner = fv[1:-1]
                                upper_values.append(f"UPPER('{inner}')")
                            else:
                                upper_values.append(f"UPPER({fv})")
                        values_str = ", ".join(upper_values)
                    else:
                        col_expr = column
                        values_str = ", ".join(formatted_values)
                    where_clauses.append(f"{col_expr} IN ({values_str})")
                    self.fields.append(column)
                    
            elif raw_key.endswith("-notin"):
                column = raw_key[:-6]
                if validate_column(column):
                    values = self._parse_list_value(value)
                    formatted_values = [self._format_value(column, v) for v in values]
                    # Apply case insensitivity to each value
                    meta = get_column_info(column)
                    if meta and meta.get("type") == "str":
                        col_expr = f"UPPER({column})"
                        upper_values = []
                        for fv in formatted_values:
                            if fv.startswith("'") and fv.endswith("'"):
                                inner = fv[1:-1]
                                upper_values.append(f"UPPER('{inner}')")
                            else:
                                upper_values.append(f"UPPER({fv})")
                        values_str = ", ".join(upper_values)
                    else:
                        col_expr = column
                        values_str = ", ".join(formatted_values)
                    where_clauses.append(f"{col_expr} NOT IN ({values_str})")
                    self.fields.append(column)
                    
            elif raw_key.endswith("-like"):
                column = raw_key[:-5]
                if validate_column(column):
                    formatted_value = self._format_value(column, value, operator="like")
                    col_expr, val_expr = self._make_case_insensitive(column, formatted_value, "LIKE")
                    where_clauses.append(f"{col_expr} LIKE {val_expr}")
                    self.fields.append(column)
                    
            elif validate_column(raw_key):
                # Exact match
                formatted_value = self._format_value(raw_key, value)
                col_expr, val_expr = self._make_case_insensitive(raw_key, formatted_value, "=")
                where_clauses.append(f"{col_expr} = {val_expr}")
                self.fields.append(raw_key)

        # Join together
        self.whereclause = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    def setGroupByClause(self, group):
        self.groupbyclause = ""
        if group is not None:
            self.groupbyclause = group 

        for key, value in self.args.items():
            if key == "-group":
                self.groupbyclause = value
        
        if self.groupbyclause != "":
            self.groupbyclause = " GROUP BY " + self.groupbyclause

    def setOrderByClause(self, order):
        self.orderbyclause = ""
        if order is not None:
            self.orderbyclause = order 

        direction = "DESC"
        if "-direction" in self.args:
            direction = self.args["-direction"]

        for key, value in self.args.items():
            if key == "-order":
                self.orderbyclause = value
        
        if self.orderbyclause != "":
            self.orderbyclause = (f" ORDER BY {self.orderbyclause} {direction}")

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
        query = self.selectclause + self.fromclause + self.whereclause + self.groupbyclause + self.orderbyclause + self.limitclause
        print(query)
        return query