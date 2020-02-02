# -*- coding: utf8 -*-

from sqlalchemy.types import TypeDecorator, TEXT
import json


class DatabaseJSONEncoder(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = TEXT
    date_fields = 'dates_converted'

    def process_bind_param(self, value, dialect):
        if value is None:
            return ''

        if isinstance(value, dict):
            value[self.date_fields] = []
            for column, obj in value.items():
                # convert datetimes objects
                if hasattr(obj, 'isoformat'):
                    value[column] = obj.isoformat()
                    value[self.date_fields].append(column)
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        result = json.loads(value)
        if isinstance(result, dict):
            if result.get(self.date_fields):
                import dateutil.parser
                for column in result.get(self.date_fields, []):
                    if result.get(column):
                        result[column] = dateutil.parser.parse(result[column])
                del result[self.date_fields]
        return result
