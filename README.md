# ChangeTracker — Python Change Tracking Utility

ChangeTracker is a library for tracking changes in Python objects of any complexity (including nested structures, lists, dicts, and custom classes).

## Installation
https://pypi.org/project/changetracker/
```bash
pip install changetracker
```

## Quick Start

### 1. Inherit your class from ChangeTracker

```python
from changetracker import ChangeTracker, ChangeTrackerLogs, ChangeTrackerLog

class Address(ChangeTracker):
    def __init__(self, city, street):
        self.city = city
        self.street = street
        super().__init__()  # required call to super().__init__() at the end of __init__

class User(ChangeTracker):
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address
        self.hobbies = ['reading']
        super().__init__()  # required call to super().__init__() at the end of __init__

def print_diff(logsData: ChangeTrackerLogs):
    for log in logsData.data:
        log: ChangeTrackerLog
        print(f"{log.field:10} | {log.action.value:8} | old: {log.old_value} | new: {log.new_value}")
```
---

### 2. Track current changes with .get_changed_data()
```python
user = User('Ivan', 25, Address('Kyiv', 'Khreshchatyk'))

# user: Change value
user.age = 26
# user: Add new field
user.email = 'ivan@example.com'
# user: Change in list
user.hobbies.append('sports')
# user: Delete field

# user.address: Delete field
del user.address.street
# user.address: Change field
user.address.city = 'Lviv'
```

```python
# user: Show changes since last .commit()
print_diff(user.get_changed_data())
```
**Output:**
```python
# field:   | action:  | diff values:
age        | changed  | old: 25 | new: 26
address    | changed  | old: {'city': 'Kyiv', 'street': 'Khreshchatyk'} | new: {'city': 'Lviv'}
email      | created  | old: None | new: 'ivan@example.com'
hobbies    | changed  | old: ['reading'] | new: ['reading', 'sports']
```

```python
# user.address: Show changes since last .commit()
print_diff(user.address.get_changed_data())
```
**Output:**
```python
# field:   | action:  | diff values:
street     | deleted  | old: 'Khreshchatyk' | new: None
city       | changed  | old: 'Kyiv' | new: 'Lviv'
```

### Commit changes with .commit()
```python
# Save all changes. All previous entries from .get_changed_data() are cleared
user.commit()

user.address.city = "Hostomel"

print_diff(user.address.get_changed_data())
```
**Output:**
```python
# field:   | action:  | diff values:
city       | changed  | old: 'Lviv' | new: 'Hostomel'
```
---

### Full change log with .get_change_log()

`get_change_log` returns the full history of committed changes (not just current diffs like `get_changed_data`).

```python
# Save all changes. All previous entries from .get_changed_data() are cleared
user.commit()
```

```python
# user: Show full change history
for log in user.get_change_log().data:
    print(f"{log.timestamp:%Y-%m-%d %H:%M:%S} | {log.commit_id} | {log.field:7} | {log.action.value:9} | old: {log.old_value} | new: {log.new_value}")
```
**Output:**
```python
# date:             | commit_id:                           | field:  | action:   | diff values:
2025-07-21 00:52:51 | 03ae3111-d41d-498f-874d-e8813581162a | age     | created   | old: None | new: 25
2025-07-21 00:52:51 | 03ae3111-d41d-498f-874d-e8813581162a | name    | created   | old: None | new: 'Ivan'
2025-07-21 00:52:51 | 03ae3111-d41d-498f-874d-e8813581162a | hobbies | created   | old: None | new: ['reading']
2025-07-21 00:52:51 | 03ae3111-d41d-498f-874d-e8813581162a | address | created   | old: None | new: {'city': 'Kyiv', 'street': 'Khreshchatyk'}

2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | age     | changed   | old: 25 | new: 26
2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | address | changed   | old: {'city': 'Kyiv', 'street': 'Khreshchatyk'} | new: {'city': 'Lviv'}
2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | email   | created   | old: None | new: 'ivan@example.com'
2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | hobbies | changed   | old: ['reading'] | new: ['reading', 'sports']

2025-07-21 01:11:52 | e59e6414-7e79-4e0f-8395-ec27d974ffe1 | address | changed   | old: {'city': 'Lviv'} | new: {'city': 'Hostomel'}
```

```python
# user.address: Show full change history
for log in user.address.get_change_log().data:
    print(f"{log.timestamp:%Y-%m-%d %H:%M:%S} | {log.commit_id} | {log.field:7} | {log.action.value:9} | old: {log.old_value} | new: {log.new_value}")
```
**Output:**
```python
# date:             | commit_id:                           | field:  | action:   | diff values:
2025-07-21 00:52:51 | 63803546-d96e-46f9-95b2-9a6554ead5f3 | street  | created   | old: None | new: 'Khreshchatyk'
2025-07-21 00:52:51 | 63803546-d96e-46f9-95b2-9a6554ead5f3 | city    | created   | old: None | new: 'Kyiv'

2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | street  | deleted   | old: 'Khreshchatyk' | new: None
2025-07-21 00:53:01 | c05cc885-c670-4075-8b6d-dbec1bdb621f | city    | changed   | old: 'Kyiv' | new: 'Lviv'

2025-07-21 01:11:52 | e59e6414-7e79-4e0f-8395-ec27d974ffe1 | city    | changed   | old: 'Lviv' | new: 'Hostomel'
```

> **Note:** `get_change_log` shows all changes that were committed via `.commit()`.

## Features
- Tracks changes at any depth
- Supports list, dict, and custom classes
- Logs type of change: create, delete, update
- Flexible field filtering (public/private/all)
- Recursively tracks nested ChangeTracker objects
- Full change history with timestamp and commit_id

## License
MIT
