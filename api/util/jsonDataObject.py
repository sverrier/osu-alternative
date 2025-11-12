import json
from datetime import datetime

class jsonDataObject:
    columns = ''
    values = ''
    # Subclasses should define these
    table = None
    key_columns = None
    json_columns = set()
    flatten_columns = set()
    column_list = []  # NEW: Define column order in subclasses

    def __init__(self, jsonObject, table, key_columns, flatten_columns, json_columns, column_list):
        self.jsonObject = jsonObject
        self.table = table 
        self.key_columns = key_columns
        self.flatten_columns = flatten_columns
        self.json_columns = json_columns
        self.column_list = column_list

        tempJsonObject = self.jsonObject.copy()

        # Flatten fields specified in FLATTEN_COLUMNS
        flattened_data = {}
        for field in self.flatten_columns:
            field_data = tempJsonObject.pop(field, {})
            
            if isinstance(field_data, dict):
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
            return "NULL"

        return "'" + value.replace("'", "''") + "'"

    def generate_insert_query(self):
        """
        Generate an INSERT SQL query for the PostgreSQL table.
        Properly escapes strings and stores specific fields as JSONB.
        """
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

    @classmethod
    def get_insert_query_template(cls):
        """
        Generalized parameterized INSERT query template.
        Uses column_list defined in subclass to determine order.
        """
        if not cls.column_list:
            raise ValueError(f"{cls.__name__} must define column_list class attribute")
        
        column_str = ", ".join(cls.column_list)
        
        # Create placeholders with JSONB casting where needed
        placeholders = []
        for i, col in enumerate(cls.column_list):
            if col in cls.json_columns:
                placeholders.append(f"${i+1}::jsonb")
            else:
                placeholders.append(f"${i+1}")
        
        placeholders_str = ", ".join(placeholders)
        
        # Generate UPDATE clause for ON CONFLICT
        set_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in cls.column_list])
        
        return f"""
            INSERT INTO {cls.table} ({column_str}) 
            VALUES ({placeholders_str}) 
            ON CONFLICT ({cls.key_columns})
            DO UPDATE SET {set_clause}
        """

    def get_insert_params(self):
        """
        Returns a tuple of values in the order defined by column_list.
        Values are properly formatted for asyncpg (no SQL escaping needed).
        """
        if not self.column_list:
            raise ValueError(f"{self.__class__.__name__} must define column_list class attribute")
        
        params = []
        for col in self.column_list:
            value = self.final_json.get(col)  # Use .get() to handle missing columns
            
            if col in self.json_columns:
                # For JSONB columns, serialize to JSON string for asyncpg
                if value is None:
                    params.append(json.dumps({}))
                else:
                    params.append(json.dumps(value))
            elif value is None:
                params.append(None)
            elif isinstance(value, bool):
                params.append(value)
            elif isinstance(value, str) and col in self.date_columns:
                # Parse ISO datetime strings for timestamp columns
                try:
                    params.append(datetime.fromisoformat(value.replace('Z', '+00:00')))
                except (ValueError, AttributeError):
                    params.append(None)
            else:
                params.append(value)
        
        return tuple(params)