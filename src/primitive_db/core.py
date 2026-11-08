"""Основная логика работы с таблицами и записями."""

from primitive_db.constants import (
    DELETE_RECORDS_ACTION,
    DROP_TABLE_ACTION,
    ID_COLUMN_NAME,
    ID_COLUMN_TYPE,
    INVALID_COLUMN_COUNT,
    INVALID_VALUE,
    TABLE_EXISTS,
    TABLE_NOT_FOUND,
    VALID_COLUMN_TYPES,
)
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.parser import convert_value
from primitive_db.utils import delete_table_data, load_table_data, save_table_data


def get_table_columns(metadata, table_name):
    """Возвращает описание столбцов таблицы."""
    if table_name not in metadata:
        raise ValueError(TABLE_NOT_FOUND.format(name=table_name))
    return metadata[table_name]["columns"]


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает таблицу и добавляет служебный столбец ID."""
    if table_name in metadata:
        raise ValueError(TABLE_EXISTS.format(name=table_name))

    prepared_columns = [{"name": ID_COLUMN_NAME, "type": ID_COLUMN_TYPE}]
    for name, column_type in columns:
        if column_type not in VALID_COLUMN_TYPES:
            raise ValueError(INVALID_VALUE.format(value=f"{name}:{column_type}"))
        prepared_columns.append({"name": name, "type": column_type})

    metadata[table_name] = {"columns": prepared_columns}
    return metadata


@handle_db_errors
@confirm_action(DROP_TABLE_ACTION)
def drop_table(metadata, table_name):
    """Удаляет таблицу и ее данные."""
    if table_name not in metadata:
        raise ValueError(TABLE_NOT_FOUND.format(name=table_name))
    del metadata[table_name]
    delete_table_data(table_name)
    return metadata


def list_tables(metadata):
    """Возвращает отсортированный список имен таблиц."""
    return sorted(metadata)


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data=None):
    """Добавляет запись в таблицу и возвращает обновленные данные."""
    columns = get_table_columns(metadata, table_name)
    if len(values) != len(columns) - 1:
        raise ValueError(INVALID_COLUMN_COUNT)

    should_save = table_data is None
    if should_save:
        table_data = load_table_data(table_name)

    new_row = {ID_COLUMN_NAME: _next_id(table_data)}
    for column, raw_value in zip(columns[1:], values):
        try:
            new_row[column["name"]] = convert_value(
                column["type"],
                raw_value,
            )
        except ValueError:
            raise ValueError(INVALID_VALUE.format(value=raw_value)) from None
    table_data.append(new_row)

    if should_save:
        save_table_data(table_name, table_data)
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Возвращает записи, подходящие под условие where."""
    if not where_clause:
        return list(table_data)
    return [
        row
        for row in table_data
        if all(row.get(name) == value for name, value in where_clause.items())
    ]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет подходящие под условие записи."""
    for row in table_data:
        if _matches(row, where_clause):
            row.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action(DELETE_RECORDS_ACTION)
def delete(table_data, where_clause):
    """Удаляет подходящие под условие записи."""
    return [row for row in table_data if not _matches(row, where_clause)]


def _matches(row, where_clause):
    """Проверяет, подходит ли запись под условие."""
    return all(row.get(name) == value for name, value in where_clause.items())


def _next_id(table_data):
    """Возвращает следующий свободный идентификатор."""
    identifiers = [row.get(ID_COLUMN_NAME, 0) for row in table_data]
    return max(identifiers, default=0) + 1
