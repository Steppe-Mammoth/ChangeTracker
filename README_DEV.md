# Інструкція для розробника

## 1. Запуск тестування

1. Встановіть залежності для розробки:
   ```bash
   pip install -r requirements.txt
   ```

2. Запустіть тести:
   ```bash
   pytest
   ```
   (Тести мають бути у папці `tests/` і починатися з `test_*.py`.)

---

## 2. Збірка пакету

1. Переконайтесь, що файл `pyproject.toml` знаходиться у корені проєкту.
2. Виконайте команду:
   ```bash
   python -m build
   ```
   Після цього у директорії `dist/` з’являться файли `.tar.gz` та `.whl` — це і є ваші дистрибутиви.

---

## 3. Публікація на PyPI

1. Зареєструйтесь на [PyPI](https://pypi.org/account/register/) (якщо ще не маєте акаунта).
2. Встановіть twine (вже у requirements.txt):
   ```bash
   pip install twine
   ```
3. Завантажте пакет на PyPI:
   ```bash
   twine upload dist/*
   ```
   Вас попросять ввести логін та пароль від PyPI.

---

### Додатково

- Для тестової публікації (на TestPyPI, щоб перевірити все перед релізом):
  ```bash
  twine upload --repository testpypi dist/*
  ```
  (Зареєструйтесь на https://test.pypi.org/)

---

**Порада:**  
Перед публікацією переконайтесь, що у вас актуальні версії build та twine:
```bash
pip install --upgrade build twine
``` 