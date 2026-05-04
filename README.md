# Курсовой проект: веб-приложение для покупки билетов на поезда

## Технологии
- Python 3
- Flask
- PostgreSQL
- unittest для тестирования

## Запуск проекта
1. Создайте базу данных PostgreSQL, например `train_tickets`.
2. Подключитесь к PostgreSQL через `psql`, `pgAdmin` или любой другой клиент.
3. Последовательно выполните SQL-скрипты:
   - `database/schema.sql`
   - `database/views.sql`
   - `database/functions.sql`
   - `database/triggers.sql`
   - `database/seed.sql`
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. При необходимости задайте переменные окружения:
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`
6. Запустите приложение:
   ```bash
   python app.py
   ```

## Запуск тестов
```bash
python -m unittest discover -s tests
```

## Что можно показать на защите
- создание таблиц, представления, функций и триггеров в PostgreSQL;
- заполнение таблиц тестовыми данными;
- поиск рейсов в веб-приложении;
- оформление билета;
- список купленных билетов;
- запуск unit-тестов.