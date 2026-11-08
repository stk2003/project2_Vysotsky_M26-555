# Primitive DB

Примитивная база данных с интерактивным интерфейсом командной строки. Проект
поддерживает создание таблиц, добавление, чтение, обновление и удаление записей,
а также хранение метаданных и данных в JSON-файлах.

## Возможности

- создание и удаление таблиц;
- автоматическое добавление столбца `ID` с типом `int`;
- поддержка типов `int`, `str` и `bool`;
- CRUD-операции: `insert`, `select`, `update`, `delete`;
- фильтрация записей по условию `where`;
- вывод таблиц через `prettytable`;
- подтверждение опасных операций;
- обработка ошибок через декораторы;
- замер времени выполнения `select` и `insert`;
- кэширование результатов `select` через замыкание;
- хранение метаданных в `db_meta.json`, данных — в `data/<таблица>.json`.

## Стек

- Python 3.12;
- [uv](https://docs.astral.sh/uv/) для управления зависимостями;
- `prompt` для ввода команд;
- `prettytable` для вывода таблиц;
- `ruff` для линтинга и форматирования.

## Структура проекта

```text
project2_Vysotsky_M26-555/
├── src/primitive_db/
│   ├── __init__.py
│   ├── main.py          # точка входа
│   ├── engine.py        # интерактивный цикл и обработка команд
│   ├── core.py          # логика работы с таблицами и записями
│   ├── parser.py        # разбор команд, значений и условий
│   ├── utils.py         # чтение и запись JSON-файлов
│   ├── decorators.py    # обработка ошибок, подтверждения, таймер, кэш
│   └── constants.py     # константы приложения
├── demo.cast            # запись демонстрации
├── Makefile
├── pyproject.toml
├── uv.lock
└── README.md
```

## Установка

```bash
uv sync
```

## Запуск

```bash
uv run database
```

> Если проект расположен в пути с кириллицей, editable-установка `uv` может
> не найти пакет. В этом случае используйте
> `uv run --no-editable database`.

Также доступна команда-синоним:

```bash
uv run project
```

При первом запуске создаются файлы `db_meta.json` и каталог `data/`. Эти файлы
добавлены в `.gitignore`, потому что содержат пользовательские данные.

## Команды

```text
<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу
<command> list_tables - показать список всех таблиц
<command> drop_table <имя_таблицы> - удалить таблицу со всеми записями
<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись
<command> select from <имя_таблицы> [where <столбец> = <значение>] - прочитать записи
<command> update <имя_таблицы> set <столбец1> = <новое_значение> where <столбец_условия> = <значение_условия> - обновить запись
<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись
<command> info <имя_таблицы> - вывести информацию о таблице
<command> exit - выйти из программы
<command> help - справочная информация
```

Строковые значения с пробелами следует заключать в кавычки:

```text
insert into users values ("Sergei Ivanov", 28, true)
```

## Пример работы

```text
Введите команду: create_table users name:str age:int is_active:bool
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int, is_active:bool
Введите команду: insert into users values ("Sergei", 28, true)
Функция insert выполнилась за 0.000 секунд.
Запись с ID=1 успешно добавлена в таблицу "users".
Введите команду: select from users
Функция select выполнилась за 0.000 секунд.
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+
Введите команду: update users set age = 29 where ID = 1
Запись с ID=1 в таблице "users" успешно обновлена.
Введите команду: delete from users where ID = 1
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Запись с ID=1 успешно удалена из таблицы "users".
```

## Демонстрация

[![Аскинема-демонстрация](https://asciinema.org/a/gGcjZVxWyPgDijt6.svg)](https://asciinema.org/a/gGcjZVxWyPgDijt6)

Ссылка на запись: <https://asciinema.org/a/gGcjZVxWyPgDijt6>

Локальная копия записи находится в файле [demo.cast](demo.cast).

## Разработка

Установка зависимостей и запуск линтера:

```bash
make install
make lint
make run
```

Или напрямую через `uv`:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run database
```

## Хранение данных

Метаданные таблиц хранятся в `db_meta.json`:

```json
{
  "users": {
    "columns": [
      {"name": "ID", "type": "int"},
      {"name": "name", "type": "str"},
      {"name": "age", "type": "int"},
      {"name": "is_active", "type": "bool"}
    ]
  }
}
```

Записи таблицы хранятся в `data/users.json` в виде списка объектов. Значения
типов `int` и `bool` сохраняются как числа и логические значения JSON.

## Автор

Высоцкий М26-555
