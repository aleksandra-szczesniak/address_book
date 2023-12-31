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
        self.fields = {"phones": [], "emails": [], "birthday": []}
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
        for record in self.data.values():
            matches_criteria = any(
                (field == 'name' and getattr(record.name, 'value', None) == criteria[field]) or
                (field in record.fields and (
                    (isinstance(record.fields[field], list) and any(criteria[field] in f.value for f in record.fields[field] if hasattr(f, 'value'))) or
                    (not isinstance(
                        record.fields[field], list) and criteria[field] in record.fields[field].value)
                ))
                for field in criteria.keys()
            )
            if matches_criteria:
                matching_records.append(record)
        return matching_records

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        with open(filename, "rb") as file:
            self.data = pickle.load(file)

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


if __name__ == "__main__":

    address_book = AddressBook()

    record1 = Record(name="Jan Kowalski", birthday="1990-05-15")
    record1.add_field("phones", "123-456-7890")
    record1.add_field("emails", "jan.kowalski@gmail.com")

    record2 = Record(name="Zofia Nowak", birthday="1985-08-22")
    record2.add_field("phones", "987-654-3210")
    record2.add_field("emails", "zofia.nowak@gmail.com")

    address_book.add_record(record1)
    address_book.add_record(record2)

    address_book.save_to_file("address_book.pkl")

    loaded_address_book = AddressBook()
    loaded_address_book.load_from_file("address_book.pkl")

    print("Wszystkie rekordy w AddressBook:")
    for record in address_book:
        print(record.__dict__)

    search_query = "Jan Kowalski"
    my_data = loaded_address_book.search(search_query)

    print(f"\nWyniki wyszukiwania dla \"{search_query}\":")
    for result in my_data:
        print(
            f"Name: {result.name.value}, Birthday: {result.fields['birthday'].value}")
