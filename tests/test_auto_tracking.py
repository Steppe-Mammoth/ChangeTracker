#!/usr/bin/env python3

# Заміна імпорту на нову назву пакету
from changetracker.core import ChangeTracker, ChangeTrackerIncludeMode

# --- Простий трекінг простих типів ---
class Simple(ChangeTracker):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        super().__init__()

# --- Вкладений ChangeTracker ---
class Address(ChangeTracker):
    def __init__(self, city):
        self.city = city
        super().__init__()

class User(ChangeTracker):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        super().__init__()

# --- Трекінг list ---
class ListHolder(ChangeTracker):
    def __init__(self, items):
        self.items = items
        super().__init__()

# --- Трекінг dict ---
class DictHolder(ChangeTracker):
    def __init__(self, d):
        self.d = d
        super().__init__()

# --- Трекінг кастомного класу ---
class Custom:
    def __init__(self, x):
        self.x = x

class CustomHolder(ChangeTracker):
    def __init__(self, c):
        self.c = c
        super().__init__()

# --- Edge-case: list із ChangeTracker ---
class Item(ChangeTracker):
    def __init__(self, value):
        self.value = value
        super().__init__()

class ListOfTrackers(ChangeTracker):
    def __init__(self, items):
        self.items = items
        super().__init__()

# --- Edge-case: dict із кастомними класами ---
class DictOfCustoms(ChangeTracker):
    def __init__(self, d):
        self.d = d
        super().__init__()

# --- Edge-case: зміна типу поля ---
class TypeChange(ChangeTracker):
    def __init__(self, f):
        self.f = f
        super().__init__()

# --- Edge-case: видалення поля ---
class Deletion(ChangeTracker):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        super().__init__()

# --- Edge-case: додавання нового поля ---
class Addition(ChangeTracker):
    def __init__(self, a):
        self.a = a
        super().__init__()

# --- Всі функції-тести ---
def test_simple():
    s = Simple(1, 'x')
    s.commit()
    s.a = 2
    changes = s.get_changed_data()
    assert any(log.field == 'a' and log.old_value == 1 and log.new_value == 2 for log in changes.data)

def test_nested_changetrackerr():
    addr = Address('Kyiv')
    user = User('Ivan', addr)
    user.commit()
    addr.city = 'Lviv'
    changes = user.get_changed_data()
    assert any('city' in str(log.new_value) for log in changes.data)

def test_list():
    lh = ListHolder([1, 2, 3])
    lh.commit()
    lh.items.append(4)
    changes = lh.get_changed_data()
    assert any(log.field == 'items' and 4 in log.new_value for log in changes.data)

def test_dict():
    dh = DictHolder({'a': 1})
    dh.commit()
    dh.d['b'] = 2
    changes = dh.get_changed_data()
    assert any(log.field == 'd' and 'b' in log.new_value for log in changes.data)

def test_custom_class():
    ch = CustomHolder(Custom(5))
    ch.commit()
    ch.c.x = 10
    changes = ch.get_changed_data()
    print("changes:", changes)
    print([log.old_value for log in changes.data if log.field == 'c'])
    print([log.new_value for log in changes.data if log.field == 'c'])
    assert any(log.field == 'c' and log.old_value['x'] == 5 and log.new_value['x'] == 10 for log in changes.data)

def test_list_of_changetrackers():
    items = [Item(1), Item(2)]
    lot = ListOfTrackers(items)
    lot.commit()
    items[0].value = 100
    changes = lot.get_changed_data()
    assert any(
        log.field == 'items'
        and isinstance(log.new_value, list)
        and any(isinstance(item, dict) and item.get('value') == 100 for item in log.new_value)
        for log in changes.data
    )

def test_dict_of_customs():
    d = {'a': Custom(1), 'b': Custom(2)}
    doc = DictOfCustoms(d)
    doc.commit()
    d['a'].x = 42
    changes = doc.get_changed_data()
    assert any(log.field == 'd' and log.old_value['a']['x'] == 1 and log.new_value['a']['x'] == 42 for log in changes.data)

def test_type_change():
    tc = TypeChange(123)
    tc.commit()
    tc.f = 'now string'
    changes = tc.get_changed_data()
    assert any(log.field == 'f' and log.old_value == 123 and log.new_value == 'now string' for log in changes.data)

def test_deletion():
    d = Deletion(1, 2)
    d.commit()
    del d.b
    changes = d.get_changed_data()
    assert any(log.field == 'b' and log.action.name == 'DELETED' for log in changes.data)

def test_addition():
    a = Addition(1)
    a.commit()
    a.b = 99
    changes = a.get_changed_data()
    assert any(log.field == 'b' and log.action.name == 'CREATED' for log in changes.data)

# --- Складний кейс: вкладеність 3+ рівнів ---
class DeepNested(ChangeTracker):
    def __init__(self, a):
        self.a = a
        super().__init__()

def test_deep_nested():
    class L2(ChangeTracker):
        def __init__(self, b):
            self.b = b
            super().__init__()
    class L3(ChangeTracker):
        def __init__(self, c):
            self.c = c
            super().__init__()
    l3 = L3(100)
    l2 = L2(l3)
    dn = DeepNested(l2)
    dn.commit()
    l3.c = 999
    changes = dn.get_changed_data()
    # Має бути зміна у вкладеному l3.c
    assert any('c' in str(log.new_value) and '999' in str(log.new_value) for log in changes.data)

# --- Складний кейс: list із dict ---
class ListOfDicts(ChangeTracker):
    def __init__(self, items):
        self.items = items
        super().__init__()

def test_list_of_dicts():
    lod = ListOfDicts([{'a': 1}, {'b': 2}])
    lod.commit()
    lod.items[1]['b'] = 22
    changes = lod.get_changed_data()
    assert any(log.field == 'items' and log.new_value[1]['b'] == 22 for log in changes.data)

# --- Складний кейс: dict із list ---
class DictOfLists(ChangeTracker):
    def __init__(self, d):
        self.d = d
        super().__init__()

def test_dict_of_lists():
    dol = DictOfLists({'x': [1, 2], 'y': [3, 4]})
    dol.commit()
    dol.d['y'].append(5)
    changes = dol.get_changed_data()
    assert any(log.field == 'd' and 5 in log.new_value['y'] for log in changes.data)

# --- Складний кейс: зміна типу у вкладеному об'єкті ---
class Holder(ChangeTracker):
    def __init__(self, val):
        self.val = val
        super().__init__()

def test_type_change_nested():
    h = Holder({'a': 1})
    h.commit()
    h.val = [1, 2, 3]
    changes = h.get_changed_data()
    assert any(log.field == 'val' and isinstance(log.old_value, dict) and isinstance(log.new_value, list) for log in changes.data)

# --- Складний кейс: одночасна зміна кількох рівнів ---
def test_multi_level_change():
    class Inner(ChangeTracker):
        def __init__(self, x):
            self.x = x
            super().__init__()
    class Outer(ChangeTracker):
        def __init__(self, inner, y):
            self.inner = inner
            self.y = y
            super().__init__()
    inner = Inner(1)
    outer = Outer(inner, 10)
    outer.commit()
    inner.x = 2
    outer.y = 20
    changes = outer.get_changed_data()
    assert any(log.field == 'inner' for log in changes.data)
    assert any(log.field == 'y' and log.old_value == 10 and log.new_value == 20 for log in changes.data)

# --- Складний кейс: зміна у вкладеному кастомному класі у dict у list ---
def test_deep_custom_in_list_dict():
    class DeepCustom:
        def __init__(self, z):
            self.z = z
    class Holder(ChangeTracker):
        def __init__(self, data):
            self.data = data
            super().__init__()
    dc = DeepCustom(5)
    h = Holder([{'obj': dc}])
    h.commit()
    dc.z = 99
    changes = h.get_changed_data()
    assert any(log.field == 'data' and log.old_value[0]['obj']['z'] == 5 and log.new_value[0]['obj']['z'] == 99 for log in changes.data)

# Додаємо виклики нових тестів у main
if __name__ == '__main__':
    test_simple()
    test_nested_changetrackerr()
    test_list()
    test_dict()
    test_custom_class()
    test_list_of_changetrackers()
    test_dict_of_customs()
    test_type_change()
    test_deletion()
    test_addition()
    test_deep_nested()
    test_list_of_dicts()
    test_dict_of_lists()
    test_type_change_nested()
    test_multi_level_change()
    test_deep_custom_in_list_dict()
    print('All tests passed!') 