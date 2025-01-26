import json

class User:
    def __init__(self, user):
        self.user = user

    def __str__(self):
        return json.dumps(self.user, indent=4)

    def generate_hybrid_insert_query(table_name, json_object, jsonb_columns):
        """
        Generate an INSERT query for a PostgreSQL table with JSONB and relational columns.
        """
        # Separate JSONB columns and standard columns
        standard_columns = {key: value for key, value in json_object.items() if key not in jsonb_columns}
        jsonb_data = {key: json_object[key] for key in jsonb_columns if key in json_object}

        # Prepare columns and values for the query
        standard_columns_part = ', '.join(f'"{key}"' for key in standard_columns.keys())
        jsonb_columns_part = ', '.join(f'"{key}"' for key in jsonb_data.keys())

        standard_values_part = ', '.join(
            f"'{value}'" if isinstance(value, str) else
            ('TRUE' if value is True else 'FALSE' if value is False else 'NULL' if value is None else str(value))
            for value in standard_columns.values()
        )
        jsonb_values_part = ', '.join(f"'{json.dumps(value)}'" for value in jsonb_data.values())

        # Combine into one query
        all_columns = f"{standard_columns_part}, {jsonb_columns_part}" if jsonb_columns_part else standard_columns_part
        all_values = f"{standard_values_part}, {jsonb_values_part}" if jsonb_values_part else standard_values_part

        query = f"INSERT INTO {table_name} ({all_columns}) VALUES ({all_values});"
        return query

    def generateInsert(self):
        table_name = "user_profiles"
        jsonb_columns = ["badges", "monthly_playcounts", "replays_watched_counts", "user_achievements"]

        # Generate the query
        query = self.generate_hybrid_insert_query(table_name, self.user, jsonb_columns)
