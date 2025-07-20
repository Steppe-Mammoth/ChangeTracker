# ChangeTracker — Python Change Tracking Utility

ChangeTracker — це гнучка бібліотека для відстеження змін у Python-об'єктах будь-якої складності (у т.ч. вкладені структури, списки, словники, кастомні класи).

## Встановлення

Склонуйте репозиторій або додайте changetracker у свій проєкт:

```bash
!todo
pip install <your-package-if-published>
```

## Швидкий старт

### 1. Наслідуйте свій клас від ChangeTracker

```python
from changetracker import ChangeTracker

class User(ChangeTracker):
    def __init__(self, name, age):
        self.name = name
        self.age = age
        super().__init__()  # обов'язковий виклик super().__init__() в кінці __init__
```

### 2. Відстежуйте актуальний diff

```python
user = User('Ivan', 25)
user.commit()  # Зберігаємо початковий стан

user.age = 26
changes = user.get_changed_data()
for log in changes.data:
    print(f"Поле: {log.field}, було: {log.old_value}, стало: {log.new_value}, тип зміни: {log.action}")
```
**Output:**
```
Поле: age, було: 25, стало: 26, тип зміни: ChangeTrackerAction.CHANGED
```

### 3. Підтримка вкладених структур

```python
class Address(ChangeTracker):
    def __init__(self, city):
        self.city = city
        super().__init__()

user = User('Ivan', 25)
user.address = Address('Kyiv')
user.commit()
user.address.city = 'Lviv'
changes = user.get_changed_data()
for log in changes.data:
    print(log)
```
**Output:**
```
ChangeTrackerLog(field='address', old_value={'city': 'Kyiv'}, new_value={'city': 'Lviv'}, action=<ChangeTrackerAction.CHANGED: 'changed'>, ...)
```

### 4. Підтримка list, dict, кастомних класів

```python
user.hobbies = ['reading', 'music']
user.commit()
user.hobbies.append('sports')
changes = user.get_changed_data()
print(changes.data[0])
```
**Output:**
```
ChangeTrackerLog(field='hobbies', old_value=['reading', 'music'], new_value=['reading', 'music', 'sports'], action=<ChangeTrackerAction.CHANGED: 'changed'>, ...)
```

```python
# Для кастомних класів:
class Custom:
    def __init__(self, x):
        self.x = x
user.custom = Custom(5)
user.commit()
user.custom.x = 10
changes = user.get_changed_data()
print(changes.data[0])
```
**Output:**
```
ChangeTrackerLog(field='custom', old_value={'x': 5}, new_value={'x': 10}, action=<ChangeTrackerAction.CHANGED: 'changed'>, ...)
```

---

## Великий приклад: різні типи змін та якісний output

```python
from changetracker import ChangeTracker

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

### Повний журнал змін (get_change_log)

`get_change_log` повертає повний журнал усіх зафіксованих змін (історію), а не лише поточні відмінності як `get_changed_data`.

```python
from changetracker import ChangeTracker

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