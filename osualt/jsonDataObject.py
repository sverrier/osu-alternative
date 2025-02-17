import json

class jsonDataObject:
    def __init__(self, json, table, flatten_columns, json_columns, ignore_columns):
        self.json = json
        self.table = table 
        self.flatten_columns = flatten_columns
        self.json_columns = json_columns
        self.ignore_columns = ignore_columns
    def __str__(self):
        return json.dumps(self.json, indent=4)

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

        # Ignore fields in IGNORE_COLUMNS
        for field in self.ignore_columns:
            self.json.pop(field, {})

        # Flatten fields specified in FLATTEN_COLUMNS
        flattened_data = {}
        for field in self.flatten_columns:
            field_data = self.json.pop(field, {})
            for key, value in field_data.items():
                flattened_data[f"{field}_{key}"] = value

        # Merge flattened columns with main data
        inter_data = {**self.json, **flattened_data}

        # Extract JSONB fields
        jsonb_data = {key: inter_data.pop(key, {}) for key in self.json_columns}

        # Merge all data together
        final_data = {**inter_data, **jsonb_data}

        # Prepare column names and values
        columns = ', '.join(f'"{col}"' for col in final_data.keys())
        values = ', '.join(
            f"'{json.dumps(value)}'::jsonb" if col in self.json_columns else
            self.escape_sql_string(value) if isinstance(value, str) else
            ('TRUE' if value is True else 'FALSE' if value is False else 'NULL' if value is None else str(value))
            for col, value in final_data.items()
        )

        # Generate SQL query
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({values});"
        return query