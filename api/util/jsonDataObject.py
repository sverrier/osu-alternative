import json

class jsonDataObject:
    columns = ''
    values = ''


    def __init__(self, jsonObject, table, key_columns, flatten_columns, json_columns):
        self.jsonObject = jsonObject
        self.table = table 
        self.key_columns = key_columns
        self.flatten_columns = flatten_columns
        self.json_columns = json_columns

        tempJsonObject = self.jsonObject.copy()

        # Flatten fields specified in FLATTEN_COLUMNS
        flattened_data = {}
        for field in self.flatten_columns:
            field_data = tempJsonObject.pop(field, {})  # Get field or default to empty dict
            
            if isinstance(field_data, dict):  # ✅ Ensure it's a dictionary before iterating
                for key, value in field_data.items():
                    flattened_data[f"{field}_{key}"] = value

        # Merge flattened columns with main data
        inter_data = {**tempJsonObject, **flattened_data}

        # Extract JSONB fields
        jsonb_data = {key: inter_data.pop(key, {}) for key in self.json_columns}

        # Merge all data together
        self.final_json = {**inter_data, **jsonb_data}


        
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

        
        # Prepare column names and values in alphabetical order
        self.columns = ', '.join(f'{col}' for col in self.final_json)

        self.values = ', '.join(
            self.escape_sql_string(f"{json.dumps(self.final_json[col], ensure_ascii=False)}")+"::jsonb" if col in self.json_columns else
            self.escape_sql_string(self.final_json[col]) if isinstance(self.final_json[col], str) else
            ('TRUE' if self.final_json[col] is True else 'FALSE' if self.final_json[col] is False else 'NULL' if self.final_json[col] is None else str(self.final_json[col]))
            for col in self.final_json
        )

        columns = self.columns.split(", ")
        set_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns])

        query = f"""
        INSERT INTO {self.table} ({self.columns}) 
        VALUES ({self.values}) 
        ON CONFLICT ({self.key_columns})
        DO UPDATE SET {set_clause};
        """
        return query
