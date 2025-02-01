import json

class Score:
    TABLE_NAME = "scores"  # Hardcoded table name
    JSONB_COLUMNS = {"mods", "current_user_attributes"}  # JSONB fields
    FLATTEN_COLUMNS = {"statistics", "maximum_statistics"}  # Flattened fields

    def __init__(self, score):
        self.score = score

    def __str__(self):
        return json.dumps(self.score, indent=4)

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
        Generate an INSERT SQL query for the PostgreSQL 'scores' table.
        Properly escapes strings and stores specific fields as JSONB.
        """

        # Remove 'user' field since we are ignoring it
        self.score.pop("user", None)

        # Extract and flatten specific fields
        flattened_data = {}
        for key in self.FLATTEN_COLUMNS:
            data = self.score.pop(key, {})
            for sub_key, sub_value in data.items():
                flattened_data[f"{key}_{sub_key}"] = sub_value

        # Extract JSONB fields
        jsonb_data = {key: self.score.pop(key, {}) for key in self.JSONB_COLUMNS}

        # Merge all data together
        final_data = {**self.score, **flattened_data, **jsonb_data}

        # Prepare column names and values
        columns = ', '.join(f'"{col}"' for col in final_data.keys())
        values = ', '.join(
            f"'{json.dumps(value)}'::jsonb" if col in self.JSONB_COLUMNS else
            self.escape_sql_string(value) if isinstance(value, str) else
            ('TRUE' if value is True else 'FALSE' if value is False else 'NULL' if value is None else str(value))
            for col, value in final_data.items()
        )

        # Generate SQL query
        query = f"INSERT INTO {self.TABLE_NAME} ({columns}) VALUES ({values});"
        return query