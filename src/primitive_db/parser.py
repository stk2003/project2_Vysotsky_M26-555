"""Разбор пользовательских команд и значений."""

from primitive_db.constants import (
    FALSE_VALUES,
    TRUE_VALUES,
    VALID_COLUMN_TYPES,
)


def parse_columns(tokens):
    """Разбирает список столбцов вида имя:тип."""
    if not tokens:
        raise ValueError("")

    columns = []
    names = set()
    for token in tokens:
        if token.count(":") != 1:
            raise ValueError(token)
        name, column_type = token.split(":")
        if not name or not column_type or column_type not in VALID_COLUMN_TYPES:
            raise ValueError(token)
        if name in names:
            raise ValueError(token)
        names.add(name)
        columns.append((name, column_type))
    return columns


def parse_values(values_text):
    """Разбирает значения из конструкции values (...)."""
    text = values_text.strip()
    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(text)

    inner = text[1:-1]
    if not inner.strip():
        return []

    values = []
    current = []
    quote = None
    escaped = False
    # Запятые внутри кавычек являются частью значения.
    for char in inner:
        if quote:
            if escaped:
                current.append(char)
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            else:
                current.append(char)
        elif char in ("'", '"'):
            quote = char
        elif char == ",":
            values.append("".join(current).strip())
            current = []
        else:
            current.append(char)

    if quote:
        raise ValueError(text)
    values.append("".join(current).strip())
    if any(value == "" for value in values):
        raise ValueError(text)
    return values


def extract_values_text(command):
    """Выделяет из команды insert текст после слова values."""
    lower_command = command.lower()
    start = 0
    while True:
        index = lower_command.find("values", start)
        if index == -1:
            break
        end = index + len("values")
        before_ok = index == 0 or not lower_command[index - 1].isalnum()
        after_ok = end == len(lower_command) or not lower_command[end].isalnum()
        if before_ok and after_ok:
            return command[end:].strip()
        start = end
    raise ValueError(command)


def parse_where(tokens, columns):
    """Разбирает условие where и приводит значение к типу столбца."""
    if len(tokens) != 3:
        raise ValueError(" ".join(tokens))
    column_name, operator, raw_value = tokens
    if operator != "=":
        raise ValueError(" ".join(tokens))
    column_type = get_column_type(columns, column_name)
    return {column_name: convert_value(column_type, raw_value)}


def parse_set(tokens, columns):
    """Разбирает присваивание set и приводит значение к типу столбца."""
    if len(tokens) != 3:
        raise ValueError(" ".join(tokens))
    column_name, operator, raw_value = tokens
    if operator != "=":
        raise ValueError(" ".join(tokens))
    column_type = get_column_type(columns, column_name)
    return {column_name: convert_value(column_type, raw_value)}


def get_column_type(columns, column_name):
    """Возвращает тип столбца по его имени."""
    for column in columns:
        if column["name"] == column_name:
            return column["type"]
    raise KeyError(column_name)


def convert_value(column_type, raw_value):
    """Приводит строковое значение к типу столбца."""
    if column_type == "int":
        try:
            return int(raw_value)
        except ValueError:
            raise ValueError(raw_value) from None

    if column_type == "bool":
        value = raw_value.lower()
        if value in TRUE_VALUES:
            return True
        if value in FALSE_VALUES:
            return False
        raise ValueError(raw_value)

    return raw_value
