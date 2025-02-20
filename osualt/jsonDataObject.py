import json

class jsonDataObject:
    columns = ''
    values = ''


    def __init__(self, jsonObject, table, flatten_columns, json_columns, ignore_columns):
        self.jsonObject = jsonObject
        self.table = table 
        self.flatten_columns = flatten_columns
        self.json_columns = json_columns
        self.ignore_columns = ignore_columns

        # Ignore fields in IGNORE_COLUMNS
        for field in self.ignore_columns:
            self.jsonObject.pop(field, {})

        # Flatten fields specified in FLATTEN_COLUMNS
        flattened_data = {}
        for field in self.flatten_columns:
            field_data = self.jsonObject.pop(field, {})
            for key, value in field_data.items():
                flattened_data[f"{field}_{key}"] = value

        # Merge flattened columns with main data
        inter_data = {**self.jsonObject, **flattened_data}

        # Extract JSONB fields
        jsonb_data = {key: inter_data.pop(key, {}) for key in self.json_columns}

        # Merge all data together
        final_data = {**inter_data, **jsonb_data}

        # Sort data alphabetically by keys
        sorted_keys = sorted(final_data.keys())
        
        # Prepare column names and values in alphabetical order
        self.columns = ', '.join(f'{col}' for col in sorted_keys)
        self.values = ', '.join(
            f"'{json.dumps(final_data[col])}'::jsonb" if col in self.json_columns else
            self.escape_sql_string(final_data[col]) if isinstance(final_data[col], str) else
            ('TRUE' if final_data[col] is True else 'FALSE' if final_data[col] is False else 'NULL' if final_data[col] is None else str(final_data[col]))
            for col in sorted_keys
        )
    def __str__(self):
        return json.dumps(self.jsonObject, indent=4)

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
        Generate an INSERT SQL query for the PostgreSQL 'user_profiles' table.
        Properly escapes strings and stores specific fields as JSONB.
        """

        # Generate SQL query
        query = f"INSERT INTO {self.table} ({self.columns}) VALUES ({self.values});"
        return query