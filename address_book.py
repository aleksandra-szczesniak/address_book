from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    pass


class Email(Field):
    pass


class Record:
    FIELD_CLASSES = {
        "phones": Phone,
        "emails": Email,
    }

    def __init__(self, name):
        if not name:
            raise ValueError("Name is required.")
        self.name = Name(name)
        self.fields = {"phones": [], "emails": []}

    def add_field(self, field_type, value):
        if field_type in self.fields and field_type in self.FIELD_CLASSES:
            field_class = self.FIELD_CLASSES[field_type]
            self.fields[field_type].append(field_class(value))

    def remove_field(self, field_type, value):
        if field_type in self.fields:
            self.fields[field_type] = [
                f for f in self.fields[field_type] if f.value != value]

    def edit_field(self, field_type, old_value, new_value):
        if field_type in self.fields:
            for field in self.fields[field_type]:
                if field.value == old_value:
                    field.value = new_value
                    break


class AddressBook(UserDict):
    def add_record(self, record):
        unique_key = record.name.value
        self.data[unique_key] = record

    def search_records(self, criteria):
        matching_records = []
        for record in self.values():
            matches_criteria = any(
                getattr(record, field, None) == criteria[field] or
                any(f.value == criteria[field] for f in record.fields[field])
                for field in criteria.keys()
            )
            if matches_criteria:
                matching_records.append(record)
        return matching_records
