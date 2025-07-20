# ChangeTracker — Python Change Tracking Utility

ChangeTracker — це бібліотека для відстеження змін у Python-об'єктах будь-якої складності (у т.ч. вкладені структури, списки, словники, кастомні класи).

## Встановлення
https://pypi.org/project/changetracker/
```bash
pip install changetracker
```

## Швидкий старт

### 1. Наслідуйте свій клас від ChangeTracker

```python
from changetracker import ChangeTracker

class Address(ChangeTracker):
    def __init__(self, city, street):
        self.city = city
        self.street = street
        super().__init__()  # обов'язковий виклик super().__init__() в кінці __init__

class User(ChangeTracker):
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address
        self.hobbies = ['reading']
        super().__init__()  # обов'язковий виклик super().__init__() в кінці __init__ 
```
---

### 2. Відстежуйте актуальний diff .get_changed_data()
```python
from changetracker import ChangeTrackerLogs, ChangeTrackerLog

def print_diff(logsData: ChangeTrackerLogs):
    for log in logsData.data:
        log: ChangeTrackerLog
        print(f"{log.field:10} | {log.action.value:8} | old: {log.old_value} | new: {log.new_value}")

```

```python
user = User('Ivan', 25, Address('Kyiv', 'Khreshchatyk'))

# user: Зміна значення
user.age = 26
# user: Додавання нового поля
user.email = 'ivan@example.com'
# user: Зміна у списку
user.hobbies.append('sports')
# user: Видалення поля 

# user.address: Видалення поля
del user.address.street
# user.address: Зміна поля
user.address.city = 'Lviv'
```

```python
# user: Відображаємо наявні зміни з останнього .commit()
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
# user.address: Відображаємо наявні зміни з останнього .commit()
print_diff(user.address.get_changed_data())
```
**Output:**
```python
# field:   | action:  | diff values:
street     | deleted  | old: 'Khreshchatyk' | new: None
city       | changed  | old: 'Kyiv' | new: 'Lviv'
```


### Фіксація змін .commit()
```python
# Збереження всіх змін. Всі попередні записи з методу .get_changed_data() - скидаються
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

### Повний журнал змін .get_change_log()

`get_change_log` повертає повний журнал усіх зафіксованих змін (історію) через .commit(), а не лише поточні відмінності як `get_changed_data`.

```python
# Збереження всіх змін. Всі попередні записи з методу .get_changed_data() - скидаються
user.commit()
```

```python
# user: Відображаємо всю історію змін
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
# user.address: Відображаємо всю історію змін
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

> **Примітка:** get_change_log показує всі зміни, які були зафіксовані через commit().

## Особливості
- Відстеження змін будь-якої вкладеності
- Підтримка list, dict, кастомних класів
- Логування типу зміни: створення, видалення, зміна
- Гнучка фільтрація полів (public/private/all)
- Рекурсивне відстеження вкладених ChangeTracker об'єктів
- Повна історія змін з timestamp та commit_id

## Ліцензія
MIT 

--- 