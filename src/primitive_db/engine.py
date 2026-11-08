"""Интерактивный движок приложения."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import (
    COLUMN_NOT_FOUND,
    HELP_LINES,
    ID_COLUMN_NAME,
    INVALID_VALUE,
    MAIN_PROMPT,
    META_FILE,
    NO_RECORDS,
    NO_TABLES,
    RECORD_DELETED,
    RECORD_INSERTED,
    RECORD_UPDATED,
    TABLE_CREATED,
    TABLE_DROPPED,
    TABLE_INFO_COLUMNS,
    TABLE_INFO_COUNT,
    TABLE_INFO_TITLE,
    TABLE_NOT_FOUND,
    UNKNOWN_FUNCTION,
    WELCOME_LINES,
)
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.decorators import create_cacher
from primitive_db.parser import (
    extract_values_text,
    parse_columns,
    parse_set,
    parse_values,
    parse_where,
)
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def welcome():
    """Выводит приветствие и краткую справку."""
    print()
    for line in WELCOME_LINES:
        print(line)


def print_help():
    """Выводит полную справку по командам."""
    for line in HELP_LINES:
        print(line)


def run():
    """Запускает основной цикл обработки команд."""
    cache = create_cacher()
    welcome()
    while True:
        try:
            command = prompt.string(MAIN_PROMPT)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            tokens = shlex.split(command)
        except ValueError:
            print(INVALID_VALUE.format(value=command))
            continue

        if not tokens:
            continue

        try:
            if not _run_command(tokens, command, cache):
                break
        except KeyError as error:
            print(COLUMN_NOT_FOUND.format(name=error.args[0]))
        except ValueError as error:
            print(INVALID_VALUE.format(value=error))
        except (EOFError, KeyboardInterrupt):
            print()
            break


def _run_command(tokens, command, cache):
    """Выполняет одну команду и сообщает, нужно ли продолжать работу."""
    name = tokens[0].lower()
    if name == "exit":
        return False
    if name == "help":
        print_help()
    elif name == "create_table":
        _create_table(tokens, command, cache)
    elif name == "list_tables":
        _list_tables(tokens, command)
    elif name == "drop_table":
        _drop_table(tokens, command, cache)
    elif name == "insert":
        _insert(tokens, command, cache)
    elif name == "select":
        _select(tokens, command, cache)
    elif name == "update":
        _update(tokens, command, cache)
    elif name == "delete":
        _delete(tokens, command, cache)
    elif name == "info":
        _info(tokens, command)
    else:
        print(UNKNOWN_FUNCTION.format(name=tokens[0]))
    return True


def _create_table(tokens, command, cache):
    """Обрабатывает команду create_table."""
    if len(tokens) < 3:
        raise ValueError(command)

    table_name = tokens[1]
    columns = parse_columns(tokens[2:])
    metadata = load_metadata(META_FILE)
    updated_metadata = create_table(metadata, table_name, columns)
    if updated_metadata is None:
        return

    save_metadata(META_FILE, updated_metadata)
    save_table_data(table_name, [])
    invalidate_cache(cache)
    prepared_columns = updated_metadata[table_name]["columns"]
    print(
        TABLE_CREATED.format(
            name=table_name,
            columns=_format_columns(prepared_columns),
        )
    )


def _list_tables(tokens, command):
    """Обрабатывает команду list_tables."""
    if len(tokens) != 1:
        raise ValueError(command)

    metadata = load_metadata(META_FILE)
    names = list_tables(metadata)
    if not names:
        print(NO_TABLES)
        return
    for name in names:
        print(f"- {name}")


def _drop_table(tokens, command, cache):
    """Обрабатывает команду drop_table."""
    if len(tokens) != 2:
        raise ValueError(command)

    table_name = tokens[1]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    updated_metadata = drop_table(metadata, table_name)
    if updated_metadata is None:
        return

    save_metadata(META_FILE, updated_metadata)
    invalidate_cache(cache)
    print(TABLE_DROPPED.format(name=table_name))


def _insert(tokens, command, cache):
    """Обрабатывает команду insert."""
    if len(tokens) < 4 or tokens[1].lower() != "into":
        raise ValueError(command)
    if not tokens[3].lower().startswith("values"):
        raise ValueError(command)

    table_name = tokens[2]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    values = parse_values(extract_values_text(command))
    table_data = load_table_data(table_name)
    updated_data = insert(metadata, table_name, values, table_data)
    if updated_data is None:
        return

    save_table_data(table_name, updated_data)
    invalidate_cache(cache)
    print(
        RECORD_INSERTED.format(
            id=updated_data[-1][ID_COLUMN_NAME],
            table=table_name,
        )
    )


def _select(tokens, command, cache):
    """Обрабатывает команду select."""
    if len(tokens) < 3 or tokens[1].lower() != "from":
        raise ValueError(command)

    table_name = tokens[2]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    columns = metadata[table_name]["columns"]
    where_clause = None
    if len(tokens) > 3:
        if len(tokens) < 7 or tokens[3].lower() != "where":
            raise ValueError(command)
        where_clause = parse_where(tokens[4:], columns)

    table_data = load_table_data(table_name)
    cache_key = (
        table_name,
        tuple(sorted(where_clause.items())) if where_clause else None,
    )
    rows = cache(
        cache_key,
        lambda: select(table_data, where_clause),
    )
    if rows is None:
        return
    _print_table(columns, rows)


def _update(tokens, command, cache):
    """Обрабатывает команду update."""
    if len(tokens) < 6:
        raise ValueError(command)

    lower_tokens = [token.lower() for token in tokens]
    if "set" not in lower_tokens or "where" not in lower_tokens:
        raise ValueError(command)

    set_index = lower_tokens.index("set")
    where_index = lower_tokens.index("where")
    if set_index != 2 or where_index <= set_index + 2:
        raise ValueError(command)

    table_name = tokens[1]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    columns = metadata[table_name]["columns"]
    set_clause = parse_set(tokens[set_index + 1 : where_index], columns)
    where_clause = parse_where(tokens[where_index + 1 :], columns)

    table_data = load_table_data(table_name)
    matched_rows = _filter_rows(table_data, where_clause)
    if not matched_rows:
        print(NO_RECORDS)
        return

    updated_data = update(table_data, set_clause, where_clause)
    if updated_data is None:
        return

    save_table_data(table_name, updated_data)
    invalidate_cache(cache)
    for row in matched_rows:
        print(
            RECORD_UPDATED.format(
                id=row[ID_COLUMN_NAME],
                table=table_name,
            )
        )


def _delete(tokens, command, cache):
    """Обрабатывает команду delete."""
    if len(tokens) < 7 or tokens[1].lower() != "from":
        raise ValueError(command)
    if tokens[3].lower() != "where":
        raise ValueError(command)

    table_name = tokens[2]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    columns = metadata[table_name]["columns"]
    where_clause = parse_where(tokens[4:], columns)
    table_data = load_table_data(table_name)
    matched_rows = _filter_rows(table_data, where_clause)
    if not matched_rows:
        print(NO_RECORDS)
        return

    updated_data = delete(table_data, where_clause)
    if updated_data is None:
        return

    save_table_data(table_name, updated_data)
    invalidate_cache(cache)
    for row in matched_rows:
        print(
            RECORD_DELETED.format(
                id=row[ID_COLUMN_NAME],
                table=table_name,
            )
        )


def _info(tokens, command):
    """Обрабатывает команду info."""
    if len(tokens) != 2:
        raise ValueError(command)

    table_name = tokens[1]
    metadata = load_metadata(META_FILE)
    if table_name not in metadata:
        print(TABLE_NOT_FOUND.format(name=table_name))
        return

    columns = metadata[table_name]["columns"]
    table_data = load_table_data(table_name)
    print(TABLE_INFO_TITLE.format(name=table_name))
    print(TABLE_INFO_COLUMNS.format(columns=_format_columns(columns)))
    print(TABLE_INFO_COUNT.format(count=len(table_data)))


def _print_table(columns, rows):
    """Выводит записи в виде таблицы."""
    table = PrettyTable()
    table.field_names = [column["name"] for column in columns]
    table.align = "c"
    for row in rows:
        table.add_row([row.get(column["name"], "") for column in columns])
    print(table)


def _filter_rows(table_data, where_clause):
    """Возвращает записи, подходящие под условие."""
    return [
        row
        for row in table_data
        if all(row.get(name) == value for name, value in where_clause.items())
    ]


def _format_columns(columns):
    """Форматирует описание столбцов для вывода."""
    return ", ".join(f"{column['name']}:{column['type']}" for column in columns)


def invalidate_cache(cache):
    """Сбрасывает кэш результатов select."""
    cache.clear()
