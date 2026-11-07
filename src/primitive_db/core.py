
from primitive_db.utils import (
    confirm_action,
    handle_db_errors,
    load_table_data,
    log_time,
    save_table_data,
)


@handle_db_errors
@log_time
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")

    metadata[table_name] = {}

    for column in columns:
        name, column_type = column.split(":")
        metadata[table_name][name] = column_type

    print(f"Таблица '{table_name}' создана")


@handle_db_errors
@confirm_action
@log_time
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    del metadata[table_name]

    from pathlib import Path

    filepath = Path("data") / f"{table_name}.json"

    if filepath.exists():
        filepath.unlink()

    print(f"Таблица '{table_name}' удалена")


@handle_db_errors
@log_time
def info(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    print(f"Структура таблицы '{table_name}':")

    for column, column_type in metadata[table_name].items():
        print(f"{column}: {column_type}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    columns = metadata[table_name]

    if len(values) != len(columns):
        raise ValueError("Количество значений не совпадает с количеством колонок")

    data = load_table_data(table_name)

    row = {}

    for (column, column_type), value in zip(columns.items(), values):
        if column == "id":
            raise ValueError("Поле id заполняется автоматически")

        if column_type == "int":
            value = int(value)
        elif column_type == "float":
            value = float(value)
        elif column_type == "bool":
            value = value.lower() == "true"
        else:
            value = str(value)

        row[column] = value

    row["id"] = len(data) + 1
    data.append(row)

    save_table_data(table_name, data)

    print("Запись добавлена")


@handle_db_errors
@log_time
def select(metadata, table_name, condition=None):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    data = load_table_data(table_name)

    if condition:
        column, value = condition
        data = [row for row in data if str(row.get(column)) == value]

    if not data:
        print("Записей не найдено")
        return

    from prettytable import PrettyTable

    table = PrettyTable()
    table.field_names = list(data[0].keys())

    for row in data:
        table.add_row(row.values())

    print(table)


@handle_db_errors
@log_time
def update(metadata, table_name, record_id, column, value):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    if column not in metadata[table_name]:
        raise ValueError(f"Колонка '{column}' не существует")

    data = load_table_data(table_name)

    for row in data:
        if str(row["id"]) == record_id:
            row[column] = value
            save_table_data(table_name, data)
            print("Запись обновлена")
            return

    raise ValueError(f"Запись с id {record_id} не найдена")


@handle_db_errors
@log_time
def delete(metadata, table_name, record_id):
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")

    data = load_table_data(table_name)

    new_data = [row for row in data if str(row["id"]) != record_id]

    if len(new_data) == len(data):
        raise ValueError(f"Запись с id {record_id} не найдена")

    save_table_data(table_name, new_data)

    print("Запись удалена")


def list_tables(metadata):
    if not metadata:
        print("База данных пуста")
        return

    print("Список таблиц:")

    for table_name in metadata:
        print(table_name)
