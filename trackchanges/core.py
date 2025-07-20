# core.py — основний код для changetracker
import copy
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Literal
import uuid



class ChangeTrackerIncludeMode(Enum):
    ALL = "__all"
    ONLY_PUBLIC = "__only_public"
    ONLY_PRIVATE = "__only_private"


class ChangeTrackerAction(Enum):
    CREATED = "created"
    DELETED = "deleted"
    CHANGED = "changed"


@dataclass
class ChangeTrackerLog:
    field: str
    old_value: any
    new_value: any
    action: ChangeTrackerAction
    init: bool = None
    timestamp: datetime = None
    commit_id: int = None


@dataclass
class ChangeTrackerLogs:
    data: list[ChangeTrackerLog]

    def get_filtered_data(self, filter_action: ChangeTrackerAction = None, filter_init: bool = None) -> list[ChangeTrackerLog]:
        """
        Повертає відфільтрований список журналів змін (ChangeTrackerLog) відповідно до заданих фільтрів.

        :param filter_action: Якщо вказано, повертає лише зміни з відповідним типом дії (створення, видалення, зміна).
        :param filter_init: 
            Якщо True — повертає лише ініціалізаційні зміни. 
            Якщо False — повертає лише зміни після ініціалізації. 
            Якщо None — повертає всі зміни незалежно від ознаки ініціалізації.
        :return: list[ChangeTrackerLog] - Відфільтрований список журналів змін.
        """
        
        data = self.data
        if filter_action is not None:
            data = [log for log in self.data if log.action == filter_action]
        
        if filter_init is not None:
            data = [log for log in self.data if log.init == filter_init]
        
        return data



def get_filtered_data(
    data: dict[str, any],
    include_mode: ChangeTrackerIncludeMode,
    include_fields: Literal[list[str], "*"] = "*",
    exclude_fields: list[str] = None
) -> dict[str, any]:
    """
    Функція get_filtered_data фільтрує словник даних відповідно до заданого режиму включення (include_mode) та списку полів (include_fields). 
    Якщо include_fields != "*", повертає лише зазначені поля. 
    Далі, залежно від режиму include_mode (ChangeTrackerIncludeMode) повертає відповідні поля
    
    :param data: Словник з даними для фільтрації.
    :param include_mode: Режим включення полів (усі, лише публічні, лише приватні).
    :param include_fields: Список полів для включення або "*" для всіх полів.
    :param exclude_fields: Список полів для виключення.
    :return: Відфільтрований словник даних.
    """
    result = {}
    for key, value in data.items():
        # Фільтрація за include_fields
        if include_fields != "*" and key not in include_fields:
            continue
        # Фільтрація за режимом
        if include_mode == ChangeTrackerIncludeMode.ONLY_PUBLIC and key.startswith("_"):
            continue
        if include_mode == ChangeTrackerIncludeMode.ONLY_PRIVATE and not key.startswith("_"):
            continue
        # Фільтрація за exclude_fields
        if exclude_fields is not None and key in exclude_fields:
            continue
        # Якщо всі умови виконані — додаємо
        result[key] = value
    return result


def get_action_change(field: str, old_data: any, new_data: any) -> ChangeTrackerAction:
    if field not in old_data and field in new_data:
        return ChangeTrackerAction.CREATED
    elif field in old_data and field not in new_data:
        return ChangeTrackerAction.DELETED
    elif field in old_data and field in new_data and old_data[field] != new_data[field]:
        return ChangeTrackerAction.CHANGED

#!todo Залишалась проблема
# - після commit() дочірнього об'єкта, батьківський об'єкт все ще думає що в дочірньому все ще є зміни 
# через те що не оновився original_data батька
class ChangeTracker:

    """
    Клас ChangeTracker призначений для відстеження змін у даних об'єкта. 
    Він дозволяє фіксувати початковий стан, зберігати історію змін (створення, оновлення, видалення полів), 
    а також фільтрувати поля для відстеження за допомогою режимів включення (ChangeTrackerIncludeMode) та списку дозволених полів. 
    Клас зберігає журнал змін із детальною інформацією про кожну зміну, 
    включаючи старе та нове значення, час зміни, тип дії та ознаку ініціалізації.
    """

    _include_mode: ChangeTrackerIncludeMode
    _original_data: dict[str, any]
    _changed_log: list[dict[str, any]]

    # Системні ключі, які не повинні бути відстежені
    _SYSTEM_KEYS = [
        "_include_mode",
        "_original_data",
        "_changed_log",
        "_SYSTEM_KEYS"
    ]

    def __init__(self, 
        include_mode: ChangeTrackerIncludeMode = ChangeTrackerIncludeMode.ONLY_PUBLIC, 
        include_fields: Literal[list[str], "*"] = "*", #!TODO
        original_data: dict[str, any] = None,
        init_commit: bool = True
    ):

        self._include_mode = include_mode
        self._original_data = {}
        self._changed_log = []


        # Автоматично викликаємо commit() під час ініціалізації
        if init_commit:
            if (original_data is None):
                original_data = self.__dict__
            else:
                pass

            self.commit(new_data=original_data, init=True)
    
    def commit(self, new_data: dict[str, any] = None, init: bool = False, commit_id: str = None, timestamp: datetime = None) -> bool:
        """
        Фіксує поточний стан відстежуваних полів об'єкта.

        :param new_data: Дані, які потрібно зафіксувати як поточний стан. Якщо не вказано, використовуються поточні атрибути об'єкта.
        :param init: Якщо True, усі поля логуються як ініціалізовані (bool, за замовчуванням False).
        :param commit_id: ID коміту. Якщо не вказано, генерується автоматично.
        :param timestamp: Час коміту. Якщо не вказано, використовується поточна дата та час.

        Опис:
            - Порівнює нові дані з попереднім збереженим станом (_original_data).
            - Для кожного поля, що змінилося, додає запис у журнал змін (_changed_log) із зазначенням старого та нового значення, часу зміни, типу дії (створення/зміна/видалення) та ознаки ініціалізації.
            - Оновлює _original_data до нового стану.
        """

        # Отримуємо нові дані
        if new_data is None:
            new_data = self.__dict__

        # Фільтруємо нові дані
        new_filtered_data = self._get_filtered_data(data=new_data)

        # Отримуємо зміни original_data -> new_filtered_data
        changed_data = self.get_changed_data(new_data=new_filtered_data, skip_filter=True)

        # Якщо немає змін - нічого не робимо
        if len(changed_data.data) == 0:
            return True


        if timestamp is None:
            timestamp = datetime.now()
        if commit_id is None:
            commit_id = str(uuid.uuid4())

        # Оновлюємо оригінальні дані
        self._original_data = {
            k: self._get_field_snapshot(v) for k, v in new_filtered_data.items()
        }    
     
        # Рекурсивно комітимо всі вкладені ChangeTracker, Зберігаючи commit_id, timestamp, init
        for key, value in self.__dict__.items():
            if isinstance(value, ChangeTracker):
                value.commit(init=init, commit_id=commit_id, timestamp=timestamp)

        for changed_log in changed_data.data:            
            # Логуємо зміни
            # Оновлюємо дані ChangeTrackerLog об'єктів. Додаємо timestamp, commit_id, init
            changed_log.timestamp = timestamp
            changed_log.commit_id = commit_id
            changed_log.init = init
            self._changed_log.append(changed_log)

        return True


    def get_changed_data(self, new_data: dict[str, any] = None, skip_filter: bool = False) -> ChangeTrackerLogs:
        """
        Повертає журнал змін між збереженим станом об'єкта та новим станом.

        :param new_data: Нові дані для порівняння. Якщо не вказано, використовуються поточні атрибути об'єкта (self.__dict__).
        :param skip_filter: Якщо True, не застосовувати фільтрацію полів (використовувати дані як є, для випадків коли дані попередньо фільтрувались).
        :return: ChangeTrackerLogs — список змін (додавання, зміна, видалення полів) з інформацією про старе та нове значення.
        
        Опис:
            - Порівнює збережені дані (_original_data) з новими (new_data).
            - Визначає, які поля були додані, змінені або видалені.
            - Для кожної зміни створює ChangeTrackerLog із деталями змін.
        """
        result = []
        # Отримуємо поточні дані, які потрібно порівняти
        if new_data is None:
            new_data = self.__dict__
        
        # Фільтруємо нові дані
        if not skip_filter:
            new_filtered_data = self._get_filtered_data(data=new_data)
        else:
            new_filtered_data = new_data

        # Отримуємо оригінальні дані з останьго коміту
        original_data = self._original_data

        # Знаходимо всі унікальні ключі з обох словників
        all_keys = set(new_filtered_data.keys()) | set(original_data.keys())

        # Порівнюємо нові та оригінальні дані
        for key in all_keys:
            old_value = original_data.get(key, None)
            new_value = new_filtered_data.get(key, None)
            new_value = self._get_field_snapshot(new_value)
            action = get_action_change(key, original_data, new_filtered_data)

            if old_value != new_value:
                result.append(ChangeTrackerLog(
                    field=key,
                    old_value=old_value,
                    new_value=new_value,
                    action=action,
                    init=None,
                    timestamp=None,
                    commit_id=None
                ))

        return ChangeTrackerLogs(data=result)

    def get_change_log(self) -> ChangeTrackerLogs:
        return ChangeTrackerLogs(data=self._changed_log)

    def _get_filtered_data(self, data: dict[str, any] = None) -> dict[str, any]:
        return get_filtered_data(
            data=data, 
            include_mode=self._include_mode, 
            exclude_fields=self._SYSTEM_KEYS
        )

    def _get_field_snapshot(self, value):
        """
        Повертає сериалізований стан ("знімок") поля, для подальшого порівння змін в мутабельних полях.

        - Якщо значення є екземпляром ChangeTracker, рекурсивно отримує його сериалізовану копію.
        - Якщо значення є списком або словником, повертає його глибоку копію.
        - Для простих типів повертає значення як є.

        Використовується для порівняння стану полів при визначенні змін.
        """
        if isinstance(value, ChangeTracker):
            # Для вкладених ChangeTracker — рекурсивно отримуємо стан
            filtered_data = value._get_filtered_data(data=value.__dict__)
            return {k: self._get_field_snapshot(v) for k, v in filtered_data.items()}
        elif isinstance(value, dict):
            return {k: self._get_field_snapshot(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._get_field_snapshot(v) for v in value]
        elif hasattr(value, "to_dict"):
            return value.to_dict()
        elif hasattr(value, "__dict__"):
            # Можна додати фільтрацію службових полів
            return {k: self._get_field_snapshot(v) for k, v in value.__dict__.items() if not k.startswith("_")}
        elif hasattr(value, "__dataclass_fields__"):
            return asdict(value)
        else:
            # Для простих типів — повертаємо як є
            return value

    # def _get_state_snapshot(self):
    #     """
    #     Повертає "знімок" (snapshot) поточного стану об'єкта ChangeTracker, 
    #     що містить усі відстежувані (несистемні) поля та їх значення.

    #     Для кожного поля:
    #     - Якщо значення є ChangeTracker, рекурсивно повертає його стан через _get_state_snapshot().
    #     - Якщо значення є list або dict, повертає глибоку копію.
    #     - Для простих типів повертає значення як є.

    #     Використовується для порівняння поточного стану об'єкта з оригінальним при визначенні змін.
    #     """
    #     filtered_data = self._get_filtered_data(data=self.__dict__)
    #     return {k: self._get_field_snapshot(v) for k, v in filtered_data.items()}


    # def __setattr__(self, key: str, value: any) -> None:
    #     old_value = getattr(self, key, None)
    #     value = wrap_value(value, self, key)
    #     object.__setattr__(self, key, value)

    #     # Оптимізований режим визначення init
    #     if not getattr(self, '_init_done', False):
    #         # Перевіряємо стек лише до першого виходу з __init__
    #         in_init = False
    #         for frame in inspect.stack():
    #             if frame.function == '__init__' and frame.frame.f_locals.get('self') is self:
    #                 in_init = True
    #                 break
    #         if not in_init:
    #             object.__setattr__(self, "_init_done", True)
    #     is_init = not getattr(self, '_init_done', False)

    #     # Логуємо тільки системні зміни (init=True)
    #     if is_init:
    #         self._log_change(key, old_value, value, init=True)

    # def _log_change(self, key: str, old_value: any, new_value: any, init: bool = False) -> None:
    #     if hasattr(self, '_changed_log'):
    #         self._changed_log.append({
    #             "date": datetime.now(),
    #             "field": key,
    #             "old_value": old_value,
    #             "new_value": new_value,
    #             "init": init
    #         })

    # def _save_original_state(self) -> None:
    #     """
    #     Зберігає поточний стан як оригінальний.
    #     Для ChangeTracker об'єктів зберігає тільки їх ID.
    #     """
    #     original_state = {}
    #     for key in self.__dict__:
    #         if key.startswith('_'):
    #             continue  # Пропускаємо системні поля
            
    #         value = getattr(self, key)
    #         if isinstance(value, ChangeTracker):
    #             # Для ChangeTracker об'єктів зберігаємо тільки ID
    #             original_state[key] = id(value)
    #         else:
    #             original_state[key] = deepcopy(value)
        
    #     self._original_data = original_state

    # def _deep_compare(self, value1: any, value2: any) -> bool:
    #     """
    #     Глибоке порівняння двох значень.
    #     Повертає True, якщо значення рівні.
    #     """
    #     if value1 is value2:
    #         return True
        
    #     if type(value1) != type(value2):
    #         return False
        
    #     if isinstance(value1, dict):
    #         if len(value1) != len(value2):
    #             return False
    #         for key in value1:
    #             if key not in value2:
    #                 return False
    #             if not self._deep_compare(value1[key], value2[key]):
    #                 return False
    #         return True
        
    #     elif isinstance(value1, list):
    #         if len(value1) != len(value2):
    #             return False
    #         for i in range(len(value1)):
    #             if not self._deep_compare(value1[i], value2[i]):
    #                 return False
    #         return True
        
    #     else:
    #         return value1 == value2

    # def _change_data(self, key: str, value: any, old_value: any = None, init: bool = False):
    #     if hasattr(self, '_changed_data'):
    #         self._changed_data[key] = value
    #         self._log_change(key, old_value, value, init=init)

    # def get_changed_data(self, exclude_init: bool = False) -> dict[str, any]:
    #     """
    #     Повертає словник змінених полів (ключ → нове значення).
    #     Для ChangeTracker об'єктів рекурсивно викликає get_changed_data.
    #     """
    #     changed_data = {}
        
    #     # Порівнюємо поточний стан з оригінальним
    #     for key, original_value in self._original_data.items():
    #         current_value = getattr(self, key, None)
            
    #         # Спеціальна обробка для ChangeTracker об'єктів
    #         if isinstance(current_value, ChangeTracker):
    #             if isinstance(original_value, int):  # ID збережений
    #                 if id(current_value) == original_value:
    #                     # ID не змінився - рекурсивно отримуємо зміни
    #                     child_changes = current_value.get_changed_data(exclude_init)
    #                     if child_changes:
    #                         changed_data[key] = child_changes
    #                 else:
    #                     # ID змінився - повертаємо весь об'єкт як словник
    #                     changed_data[key] = self._object_to_dict(current_value)
    #             else:
    #                 # Неочікуваний тип - порівнюємо як звичайно
    #                 if not self._deep_compare(current_value, original_value):
    #                     changed_data[key] = current_value
    #         else:
    #             # Звичайне порівняння для не-ChangeTracker об'єктів
    #             if not self._deep_compare(current_value, original_value):
    #                 changed_data[key] = current_value
        
    #     return changed_data

    # def _object_to_dict(self, obj: 'ChangeTracker') -> dict:
    #     """
    #     Конвертує ChangeTracker об'єкт у словник без системних полів.
    #     """
    #     result = {}
    #     for key, value in obj.__dict__.items():
    #         if key.startswith('_'):
    #             continue  # Пропускаємо системні поля
            
    #         if isinstance(value, ChangeTracker):
    #             result[key] = self._object_to_dict(value)
    #         else:
    #             result[key] = deepcopy(value)
        
    #     return result

    # def _update_child_original_data(self, field: str, new_id: int) -> None:
    #     """
    #     Оновлює ID дочірнього ChangeTracker об'єкта в _original_data.
    #     """
    #     if field in self._original_data:
    #         self._original_data[field] = new_id

    # def get_change_log(self) -> list[dict[str, any]]:
    #     """
    #     Повертає журнал змін, порівнюючи поточний стан з _original_data.
    #     Включає системні зміни (init=True) та виявлені зміни.
    #     """
    #     change_log = deepcopy(self._changed_log)  # Системні зміни
    #     return change_log

    # def commit(self) -> None:
    #     """
    #     Зберігає поточний стан як новий базовий стан.
    #     Викликає commit() у всіх дочірніх ChangeTracker об'єктах.
    #     Оновлює _original_data у батьківському об'єкті.
    #     """
    #     # Викликаємо commit() у всіх дочірніх ChangeTracker об'єктах
    #     for key, value in self.__dict__.items():
    #         if key.startswith('_'):
    #             continue
    #         if isinstance(value, ChangeTracker):
    #             value.commit()
        
    #     # Зберігаємо поточний стан
    #     self._save_original_state()
    #     self._changed_log.clear()
        
    #     # Оновлюємо _original_data у батьківському об'єкті
    #     if self._parent and self._field:
    #         self._parent._update_child_original_data(self._field, id(self))



    # def __repr__(self) -> str:
    #     return f"{self.__class__.__name__}({self.__dict__})" 