"""Декораторы для обработки ошибок, подтверждений и замера времени."""

import time

import prompt

from primitive_db.constants import (
    COLUMN_NOT_FOUND,
    CONFIRM_TEMPLATE,
    FILE_ERROR,
    OPERATION_CANCELLED,
    UNEXPECTED_ERROR,
)


def handle_db_errors(function):
    """Перехватывает ошибки работы с базой данных."""

    def wrapper(*args, **kwargs):
        """Вызывает функцию и перехватывает ошибки базы данных."""
        try:
            return function(*args, **kwargs)
        except FileNotFoundError:
            print(FILE_ERROR)
        except KeyError as error:
            print(COLUMN_NOT_FOUND.format(name=error.args[0]))
        except ValueError as error:
            print(str(error))
        except Exception as error:
            print(UNEXPECTED_ERROR.format(error=error))
        return None

    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper


def confirm_action(action_name):
    """Создает декоратор, который запрашивает подтверждение действия."""

    def decorator(function):
        """Оборачивает функцию запросом подтверждения."""

        def wrapper(*args, **kwargs):
            """Запрашивает подтверждение и вызывает функцию."""
            answer = prompt.string(CONFIRM_TEMPLATE.format(action_name))
            if answer.strip().lower() != "y":
                print(OPERATION_CANCELLED)
                return None
            return function(*args, **kwargs)

        wrapper.__name__ = function.__name__
        wrapper.__doc__ = function.__doc__
        return wrapper

    return decorator


def log_time(function):
    """Выводит время выполнения функции."""

    def wrapper(*args, **kwargs):
        """Измеряет время выполнения функции."""
        started_at = time.monotonic()
        result = function(*args, **kwargs)
        elapsed = time.monotonic() - started_at
        print(f"Функция {function.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    return wrapper


def create_cacher():
    """Создает замыкание для кэширования результатов."""
    cache = {}

    def cache_result(key, value_function):
        """Возвращает значение из кэша или вычисляет его."""
        if key not in cache:
            cache[key] = value_function()
        return cache[key]

    def clear_cache():
        """Очищает кэш."""
        cache.clear()

    cache_result.clear = clear_cache
    return cache_result
