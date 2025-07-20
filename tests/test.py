from trackchanges.core import ChangeTracker, ChangeTrackerIncludeMode, ChangeTrackerLogs

class User1(ChangeTracker):
    def __init__(self, name: str, age: int):
        self.name=name
        self.age=age


class User2(ChangeTracker):
    def __init__(self, name: str, age: int):
        self.name=name
        self.age=age
        super().__init__()


u1 = User1(name="Ivan", age=20)
u2 = User2(name="Petro", age=21)

# print(u2.get_change_log())
# print(u2.get_filtered_data())
# u2.test = True
# print(u2.get_changed_data())
# delattr(u2, "age")
# u2.commit()
# print(u2.get_changed_data())

class Address(ChangeTracker):
    def __init__(self, city):
        self.city = city
        super().__init__()

class User(ChangeTracker):
    def __init__(self, name, address):
        self.name = name
        self.address = address
        super().__init__()

addr = Address("Kyiv")
print(id(addr), addr)

user = User("Ivan", addr)
print(id(addr), addr)
print(id(user.address), user.address)
# user.commit()

# addr.city = "Lviv"
print(user.get_changed_data())

# u1.commit()
# u2.commit()