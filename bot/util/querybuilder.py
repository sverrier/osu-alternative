from bot.util.schema import (
    validate_column,
    get_column_info,
    get_table_for_column,
    get_all_columns,
)
from bot.util.helpers import *
import re


class QueryBuilder:
    def __init__(self, args, columns=None, table=None, group=None, order=None, limit=None):
        self.args = args or {}
        self.tables = set()

        # Optional base table hint
        if table is not None:
            self.tables.add(table)

        self.setSelectClause(columns or "*")
        self.setWhereClause()
        self.setFromClause(table)
        self.setGroupByClause(group)
        self.setOrderByClause(order)
        self.setLimitClause(limit)

    # ------------------------------------------------------------------
    # Core column / schema helpers
    # ------------------------------------------------------------------
    def _register_column(self, column: str):
        """
        Record which table this column belongs to, without changing SQL.
        """
        # Already qualified: table.column
        if "." in column:
            table, _ = column.split(".", 1)
            if table:
                self.tables.add(table)
            return

        meta = get_column_info(column)
        table = meta.get("table") if meta else None

        if table is None:
            table = get_table_for_column(column)

        if table:
            self.tables.add(table)

    def _column_sql(self, column: str) -> str:
        """
        Return the SQL text to use for a logical column:
          - If schema defines an 'expression', use that.
          - Otherwise, just return the bare column name.
        Also registers the owning table in self.tables.
        """
        # Qualified case: respect it as-is, but still register the table
        if "." in column:
            table, _ = column.split(".", 1)
            if table:
                self.tables.add(table)
            return column

        meta = get_column_info(column)
        expr = meta.get("expression") if meta else None
        table = meta.get("table") if meta else None

        if table is None:
            table = get_table_for_column(column)

        if table:
            self.tables.add(table)

        # Derived / virtual columns use their expression
        if expr:
            return expr

        # Normal column: no qualification
        return column

    def _process_columns_with_aliases(self, clause_string: str) -> str:
        """
        Process a comma-separated SELECT / GROUP / ORDER clause string,
        replacing bare logical column names with expressions (if any),
        while recording table usage.
        """
        if not clause_string or clause_string.strip() == "":
            return clause_string

        parts = [p.strip() for p in clause_string.split(",")]
        all_columns = get_all_columns()
        processed_parts = []

        for part in parts:
            # Split out optional alias
            m = re.split(r"\s+AS\s+|\s+as\s+", part)
            expr = m[0].strip()
            alias = m[1].strip() if len(m) > 1 else None

            # If the whole expr is a single column
            if validate_column(expr):
                expr_sql = self._column_sql(expr)
            else:
                # More complex expression: substitute any known column tokens
                expr_sql = expr
                for col in all_columns:
                    pattern = r"\b" + re.escape(col) + r"\b"
                    if re.search(pattern, expr_sql):
                        col_sql = self._column_sql(col)
                        expr_sql = re.sub(pattern, col_sql, expr_sql)

            if alias:
                processed_parts.append(f"{expr_sql} AS {alias}")
            else:
                processed_parts.append(expr_sql)

        return ", ".join(processed_parts)

    # ------------------------------------------------------------------
    # Value / comparison helpers
    # ------------------------------------------------------------------
    def _format_value(self, column, value, operator=None):
        """
        Format a value for SQL based on the column type (from schema).
        """
        meta = get_column_info(column)
        if not meta:
            return f"'{value}'"

        col_type = meta.get("type")

        if col_type in ("int", "float", "bool"):
            return str(value)
        elif col_type in ("datetime", "timestamp"):
            return f"'{value}'"
        elif col_type == "str":
            if operator == "like":
                return f"'%{value}%'"
            return f"'{value}'"
        elif col_type in ("jsonb", "array"):
            return str(value)
        else:
            return f"'{value}'"

    def _make_case_insensitive(self, column_sql, formatted_value, operator):
        """
        Apply UPPER(...) around string columns for case-insensitive comparisons.
        We only look up metadata by the logical column name, so callers must pass
        the logical name to _format_value, but the SQL expression to wrap here.
        """
        # If column_sql is just a logical column name, we can detect its type.
        logical_name = column_sql.split(".")[-1] if "." in column_sql else column_sql
        meta = get_column_info(logical_name)

        if meta and meta.get("type") == "str":
            if formatted_value.startswith("'") and formatted_value.endswith("'"):
                inner = formatted_value[1:-1]
                return f"UPPER({column_sql})", f"UPPER('{inner}')"
            return f"UPPER({column_sql})", f"UPPER({formatted_value})"

        return column_sql, formatted_value

    def _parse_list_value(self, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",")]
        return [value]

    # ------------------------------------------------------------------
    # Clauses
    # ------------------------------------------------------------------
    def setSelectClause(self, columns):
        processed = self._process_columns_with_aliases(columns)
        self.selectclause = "SELECT " + processed

    def setFromClause(self, table):
        # Base table hint, if any
        if table is not None:
            self.tables.add(table)

        if not self.tables:
            raise ValueError("No tables inferred for query and no base table provided")

        table_order = sorted(self.tables)
        if "scoreLive" in table_order:
            table_order.remove("scoreLive")
            table_order.insert(0, "scoreLive")

        self.fromclause = f" FROM {table_order[0]}"
        joined_tables = {table_order[0]}

        for current_table in table_order[1:]:
            found_join = False
            for prev_table in list(joined_tables):
                key = f"{prev_table},{current_table}"
                reverse_key = f"{current_table},{prev_table}"

                if key in JOIN_CLAUSES:
                    self.fromclause += JOIN_CLAUSES[key]
                    joined_tables.add(current_table)
                    found_join = True
                    break
                elif reverse_key in JOIN_CLAUSES:
                    self.fromclause += JOIN_CLAUSES[reverse_key]
                    joined_tables.add(current_table)
                    found_join = True
                    break

            if not found_join:
                raise ValueError(f"Missing join condition for {current_table}")

    def setWhereClause(self):
        where_clauses = []

        for key, value in self.args.items():
            # 1) Valueless params
            if key in VALUELESS_PARAMS:
                clause, deps = VALUELESS_PARAMS[key]
                where_clauses.append(clause)
                for dep in deps:
                    self._register_column(dep)
                continue

            # 2) Special boolean variant
            if key == "-is_fa":
                key = f"-is_fa-{value.lower()}"

            # 3) Handled via VALUED_PARAMS templates
            if key in VALUED_PARAMS:
                template, deps = VALUED_PARAMS[key]

                if deps and len(deps) > 0:
                    formatted_value = self._format_value(deps[0], value)
                else:
                    formatted_value = str(value)

                if key == "-tags":
                    formatted_value = f"'%{value}%'"

                clause = template.format(value=formatted_value)
                where_clauses.append(clause)

                for dep in deps:
                    self._register_column(dep)
                continue

            # 4) Generic suffix handling
            raw_key = key.lstrip("-")

            if raw_key.endswith("-min"):
                column = raw_key[:-4]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    formatted = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(col_sql, formatted, ">=")
                    where_clauses.append(f"{col_expr} >= {val_expr}")

            elif raw_key.endswith("-max"):
                column = raw_key[:-4]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    formatted = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(col_sql, formatted, "<")
                    where_clauses.append(f"{col_expr} < {val_expr}")

            elif raw_key.endswith("-not"):
                column = raw_key[:-4]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    formatted = self._format_value(column, value)
                    col_expr, val_expr = self._make_case_insensitive(col_sql, formatted, "!=")
                    where_clauses.append(f"{col_expr} != {val_expr}")

            elif raw_key.endswith("-in"):
                column = raw_key[:-3]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    values = self._parse_list_value(value)
                    formatted_values = [self._format_value(column, v) for v in values]

                    meta = get_column_info(column)
                    if meta and meta.get("type") == "str":
                        col_expr = f"UPPER({col_sql})"
                        upper_values = []
                        for fv in formatted_values:
                            if fv.startswith("'") and fv.endswith("'"):
                                inner = fv[1:-1]
                                upper_values.append(f"UPPER('{inner}')")
                            else:
                                upper_values.append(f"UPPER({fv})")
                        values_str = ", ".join(upper_values)
                    else:
                        col_expr = col_sql
                        values_str = ", ".join(formatted_values)

                    where_clauses.append(f"{col_expr} IN ({values_str})")

            elif raw_key.endswith("-notin"):
                column = raw_key[:-6]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    values = self._parse_list_value(value)
                    formatted_values = [self._format_value(column, v) for v in values]

                    meta = get_column_info(column)
                    if meta and meta.get("type") == "str":
                        col_expr = f"UPPER({col_sql})"
                        upper_values = []
                        for fv in formatted_values:
                            if fv.startswith("'") and fv.endswith("'"):
                                inner = fv[1:-1]
                                upper_values.append(f"UPPER('{inner}')")
                            else:
                                upper_values.append(f"UPPER({fv})")
                        values_str = ", ".join(upper_values)
                    else:
                        col_expr = col_sql
                        values_str = ", ".join(formatted_values)

                    where_clauses.append(f"{col_expr} NOT IN ({values_str})")

            elif raw_key.endswith("-like"):
                column = raw_key[:-5]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    formatted = self._format_value(column, value, operator="like")
                    col_expr, val_expr = self._make_case_insensitive(col_sql, formatted, "LIKE")
                    where_clauses.append(f"{col_expr} LIKE {val_expr}")

            elif raw_key.endswith("-regex"):
                column = raw_key[:-6]
                if validate_column(column):
                    col_sql = self._column_sql(column)
                    formatted = self._format_value(column, value)
                    where_clauses.append(f"{col_sql} ~* {formatted}")

            elif validate_column(raw_key):
                # Exact match
                col_sql = self._column_sql(raw_key)
                formatted = self._format_value(raw_key, value)
                col_expr, val_expr = self._make_case_insensitive(col_sql, formatted, "=")
                where_clauses.append(f"{col_expr} = {val_expr}")

        self.whereclause = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    def setGroupByClause(self, group):
        self.groupbyclause = ""
        if group is not None:
            self.groupbyclause = group

        for key, value in self.args.items():
            if key == "-group":
                self.groupbyclause = value

        if self.groupbyclause:
            processed = self._process_columns_with_aliases(self.groupbyclause)
            self.groupbyclause = " GROUP BY " + processed

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

        if self.orderbyclause:
            processed = self._process_columns_with_aliases(self.orderbyclause)
            self.orderbyclause = f" ORDER BY {processed} {direction}"

    def setLimitClause(self, limit):
        self.limitclause = ""
        if limit is not None:
            self.limitclause = limit

        for key, value in self.args.items():
            if key == "-hardlimit":
                self.limitclause = value

        if self.limitclause:
            self.limitclause = " LIMIT " + self.limitclause

    def getQuery(self):
        query = (
            self.selectclause
            + self.fromclause
            + self.whereclause
            + self.groupbyclause
            + self.orderbyclause
            + self.limitclause
        )
        print(query)
        return query
