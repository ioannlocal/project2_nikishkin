
import json
import time
from functools import wraps
from pathlib import Path


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, FileNotFoundError) as error:
            print(f"Ошибка базы данных: {error}")
            return None

    return wrapper


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()

        try:
            return func(*args, **kwargs)
        finally:
            elapsed_time = time.perf_counter() - start_time
            print(f"Время выполнения {func.__name__}: {elapsed_time:.6f} сек.")

    return wrapper


def confirm_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        answer = input(
            f"Ты действительно хочешь выполнить действие '{func.__name__}'? (y/n): "
        )

        if answer.lower() != "y":
            print("Действие отменено")
            return None

        return func(*args, **kwargs)

    return wrapper


def create_cache():
    cache = {}

    def get_or_compute(key, compute_func):
        if key in cache:
            print("Результат получен из кэша")
            return cache[key]

        result = compute_func()
        cache[key] = result

        print("Результат сохранён в кэш")
        return result

    return get_or_compute


def load_metadata(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    filepath = Path("data") / f"{table_name}.json"

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    Path("data").mkdir(exist_ok=True)
    filepath = Path("data") / f"{table_name}.json"

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
