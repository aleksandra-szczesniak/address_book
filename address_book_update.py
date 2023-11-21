from collections import UserDict
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate_phone()

    def validate_phone(self):
        allowed_chars = set("0123456789+-()/. ")
        if not all(char in allowed_chars for char in self.value):
            raise ValueError("Invalid phone number format")

        if len([char for char in self.value if char.isdigit()]) < 9:
            raise ValueError("Phone number is too short")


class Email(Field):
    pass


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate_birthday()

    def validate_birthday(self):
        try:
            datetime.strptime(str(self.value), '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid birthday format")


class Record:
    FIELD_CLASSES = {
        "phones": Phone,
        "emails": Email,
        "birthday": Birthday,
    }

    def __init__(self, name, birthday=None):
        if not name:
            raise ValueError("Name is required.")
        self.name = Name(name)
        self.fields = {"phones": [], "emails": []}
        if birthday:
            self.add_field("birthday", birthday)

    def add_field(self, field_type, value):
        if field_type in self.fields and field_type in self.FIELD_CLASSES:
            field_class = self.FIELD_CLASSES[field_type]
            self.fields[field_type] = field_class(value)

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

    def days_to_birthday(self):
        if "birthday" in self.fields:
            today = datetime.now()
            next_birthday = datetime(
                today.year + 1, self.fields["birthday"].value.month, self.fields["birthday"].value.day)
        days_left = (next_birthday - today).days
        return days_left if days_left > 0 else 365 + days_left


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

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(filename):
        with open(filename, "rb") as file:
            pickle.load(file)

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < len(self.data):
            record = list(self.data.values())[self._iter_index]
            self._iter_index += 1
            return record
        else:
            raise StopIteration

    def search(self, query):
        criteria = {
            "name": query,
            "phones": query,
            "emails": query,
            "birthday": query,
        }
        return self.search_records(criteria)
