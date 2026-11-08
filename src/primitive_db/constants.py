"""Константы приложения primitive_db."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
DATA_FILE_TEMPLATE = "{table_name}.json"

ID_COLUMN_NAME = "ID"
ID_COLUMN_TYPE = "int"
VALID_COLUMN_TYPES = ("int", "str", "bool")
TRUE_VALUES = ("true", "1", "yes")
FALSE_VALUES = ("false", "0", "no")

MAIN_PROMPT = "Введите команду: "
CONFIRM_TEMPLATE = 'Вы уверены, что хотите выполнить "{}"? [y/n]: '
DROP_TABLE_ACTION = "удаление таблицы"
DELETE_RECORDS_ACTION = "удаление записей"

WELCOME_LINES = (
    "***",
    "<command> exit - выйти из программы",
    "<command> help - справочная информация",
)

HELP_LINES = (
    "***Процесс работы с таблицей***",
    "Функции:",
    "<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу",
    "<command> list_tables - показать список всех таблиц",
    "<command> drop_table <имя_таблицы> - удалить таблицу со всеми записями",
    "***База данных***",
    "Функции:",
    "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
    "- создать запись",
    "<command> select from <имя_таблицы> [where <столбец> = <значение>] "
    "- прочитать записи",
    "<command> update <имя_таблицы> set <столбец1> = <новое_значение> "
    "where <столбец_условия> = <значение_условия> - обновить запись",
    "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись",
    "<command> info <имя_таблицы> - вывести информацию о таблице",
    "<command> exit - выйти из программы",
    "<command> help - справочная информация",
)

TABLE_CREATED = 'Таблица "{name}" успешно создана со столбцами: {columns}'
TABLE_DROPPED = 'Таблица "{name}" успешно удалена.'
TABLE_EXISTS = 'Ошибка: Таблица "{name}" уже существует.'
TABLE_NOT_FOUND = 'Ошибка: Таблица "{name}" не существует.'
COLUMN_NOT_FOUND = 'Ошибка: Столбец "{name}" не существует.'
INVALID_VALUE = "Некорректное значение: {value}. Попробуйте снова."
INVALID_COLUMN_COUNT = (
    "Ошибка: Количество значений не совпадает с количеством столбцов."
)
UNKNOWN_FUNCTION = "Функции {name} нет. Попробуйте снова."
NO_RECORDS = "Записи не найдены."
NO_TABLES = "Таблиц пока нет."
OPERATION_CANCELLED = "Операция отменена."
FILE_ERROR = "Ошибка: Не удалось прочитать файл данных."
UNEXPECTED_ERROR = "Произошла непредвиденная ошибка: {error}"

RECORD_INSERTED = 'Запись с ID={id} успешно добавлена в таблицу "{table}".'
RECORD_UPDATED = 'Запись с ID={id} в таблице "{table}" успешно обновлена.'
RECORD_DELETED = 'Запись с ID={id} успешно удалена из таблицы "{table}".'

TABLE_INFO_TITLE = "Таблица: {name}"
TABLE_INFO_COLUMNS = "Столбцы: {columns}"
TABLE_INFO_COUNT = "Количество записей: {count}"
