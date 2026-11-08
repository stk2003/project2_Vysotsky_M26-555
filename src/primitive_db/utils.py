"""Вспомогательные функции для работы с файлами базы данных."""

import json
import os

from primitive_db.constants import DATA_DIR, DATA_FILE_TEMPLATE, META_FILE


def load_metadata(filepath=META_FILE):
    """Загружает метаданные таблиц из JSON-файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Сохраняет метаданные таблиц в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_table_path(table_name):
    """Возвращает путь к файлу с данными таблицы."""
    filename = DATA_FILE_TEMPLATE.format(table_name=table_name)
    return os.path.join(DATA_DIR, filename)


def load_table_data(table_name):
    """Загружает записи таблицы из JSON-файла."""
    try:
        with open(get_table_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, table_data):
    """Сохраняет записи таблицы в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(get_table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(table_data, file, ensure_ascii=False, indent=2)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы, если он существует."""
    try:
        os.remove(get_table_path(table_name))
    except FileNotFoundError:
        pass
