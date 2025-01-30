import json

class User:
    TABLE_NAME = "user_profiles"  # Hardcoded table name

    JSONB_COLUMNS = {"badges", "monthly_playcounts", "replays_watched_counts", "user_achievements"}

    def __init__(self, user):
        self.user = user

    def __str__(self):
        return json.dumps(self.user, indent=4)

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

        # Extract JSONB fields
        jsonb_data = {key: self.user.pop(key, {}) for key in self.JSONB_COLUMNS}

        # Merge all data together
        final_data = {**self.user, **jsonb_data}

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
