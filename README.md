# TrackChanges — Python Change Tracking Utility

TrackChanges — це гнучка бібліотека для відстеження змін у Python-об'єктах будь-якої складності (у т.ч. вкладені структури, списки, словники, кастомні класи).

## Встановлення

Склонуйте репозиторій або додайте trackchanges у свій проєкт:

```bash
pip install <your-package-if-published>
# або вручну додайте trackchanges/ у PYTHONPATH
```

## Швидкий старт

### 1. Наслідуйте свій клас від ChangeTracker

```python
from trackchanges.core import ChangeTracker

class User(ChangeTracker):
    def __init__(self, name, age):
        self.name = name
        self.age = age
        super().__init__()  # обов'язковий виклик super().__init__() в кінці __init__
```

### 2. Відстежуйте актуальний diff

```python
from trackchanges.core import ChangeTracker

class Address(ChangeTracker):
    def __init__(self, city, street):
        self.city = city
        self.street = street
        super().__init__()

class User(ChangeTracker):
    def __init__(self, name, age, address):
        self.name = name
        self.age = age
        self.address = address
        self.hobbies = ['reading']
        super().__init__()

user = User('Ivan', 25, Address('Kyiv', 'Khreshchatyk'))

# Зміна значення
user.age = 26
# Додавання нового поля
user.email = 'ivan@example.com'
# Видалення поля
del user.address.street
# Зміна у вкладеному ChangeTracker
user.address.city = 'Lviv'
# Зміна у списку
user.hobbies.append('sports')

changes = user.get_changed_data()
for log in changes.data:
    print(f"{log.field:10} | {log.action.value:8} | old: {log.old_value} | new: {log.new_value}")
```
**Output:**
```
age        | changed  | old: 25 | new: 26
email      | created  | old: None | new: ivan@example.com
street     | deleted  | old: Khreshchatyk | new: None
address    | changed  | old: {'city': 'Kyiv', 'street': 'Khreshchatyk'} | new: {'city': 'Lviv'}
hobbies    | changed  | old: ['reading'] | new: ['reading', 'sports']
```

```python
# Збереження всіх змін
user.commit()

changes = user.get_changed_data()
print(changes)
```
**Output:**
```
[] # Після .commit() старі зміни зникають, тепер будуть відображені лише нові
```
---


---

### Повний журнал змін (get_change_log)

`get_change_log` повертає повний журнал усіх зафіксованих змін (історію), а не лише поточні відмінності як `get_changed_data`.

```python
from trackchanges.core import ChangeTracker

class User(ChangeTracker):
    def __init__(self, name, age):
        self.name = name
        self.age = age
        super().__init__()

user = User('Ivan', 25)
user.commit()
user.age = 26
user.commit()  # фіксуємо зміну
user.age = 27
user.commit()  # ще одна зміна

for log in user.get_change_log().data:
    print(f"{log.timestamp:%Y-%m-%d %H:%M:%S} | {log.field:5} | {log.action.value:7} | old: {log.old_value} | new: {log.new_value}")
```
**Output:**
```
2024-05-01 12:00:01 | age   | changed | old: 25 | new: 26
2024-05-01 12:00:02 | age   | changed | old: 26 | new: 27
```

> **Примітка:** get_change_log показує всі зміни, які були зафіксовані через commit().

## Особливості
- Відстеження змін будь-якої вкладеності
- Підтримка list, dict, кастомних класів
- Логування типу зміни: створення, видалення, зміна
- Гнучка фільтрація полів (public/private/all)


## Ліцензія
MIT 

--- 