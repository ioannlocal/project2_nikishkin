import shlex

import prompt

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.utils import load_metadata, save_metadata


def welcome():
    name = prompt.string("Как тебя зовут? ")
    print(f"Привет, {name}! Добро пожаловать в Primitive DB!")
    print("Первая попытка запустить проект!")
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def run():
    metadata = load_metadata("db_meta.json")

    while True:
        try:
            command = input("Введите команду: ").strip()

            if not command:
                continue

            parts = shlex.split(command)

            if parts[0] == "exit":
                print("До свидания!")
                break

            elif parts[0] == "help":
                print("Доступные команды:")
                print("create_table <имя> <колонка:тип> ...")
                print("drop_table <имя>")
                print("list_tables")
                print("info <таблица>")
                print("insert into <таблица> values (<значения>)")
                print("select from <таблица>")
                print("select from <таблица> where <колонка> = <значение>")
                print("update <таблица> set <колонка> = <значение> where id = <id>")
                print("delete from <таблица> where id = <id>")
                print("exit")

            elif parts[0] == "create_table":
                if len(parts) < 3:
                    raise ValueError(
                        "Укажи имя таблицы и хотя бы одну колонку"
                    )

                create_table(metadata, parts[1], parts[2:])
                save_metadata("db_meta.json", metadata)

            elif parts[0] == "drop_table":
                if len(parts) != 2:
                    raise ValueError("Укажи имя таблицы")

                drop_table(metadata, parts[1])
                save_metadata("db_meta.json", metadata)

            elif parts[0] == "list_tables":
                list_tables(metadata)

            elif parts[0] == "info":
                if len(parts) != 2:
                    raise ValueError("Укажи имя таблицы")

                info(metadata, parts[1])

            elif parts[0] == "insert":
                if (
                    len(parts) < 5
                    or parts[1] != "into"
                    or parts[3] != "values"
                ):
                    raise ValueError(
                        "Используй: insert into <таблица> values (<значения>)"
                    )

                values_text = " ".join(parts[4:]).strip()
                values_text = values_text.removeprefix("(").removesuffix(")")

                values = [
                    value.strip().strip('"').strip("'")
                    for value in values_text.split(",")
                ]

                insert(metadata, parts[2], values)

            elif parts[0] == "select":
                if len(parts) == 3 and parts[1] == "from":
                    select(metadata, parts[2])

                elif (
                    len(parts) == 7
                    and parts[1] == "from"
                    and parts[3] == "where"
                    and parts[5] == "="
                ):
                    select(
                        metadata,
                        parts[2],
                        (parts[4], parts[6]),
                    )

                else:
                    raise ValueError(
                        "Используй: select from <таблица> "
                        "или select from <таблица> where <колонка> = <значение>"
                    )

            elif parts[0] == "update":
                if (
                    len(parts) != 10
                    or parts[2] != "set"
                    or parts[4] != "="
                    or parts[6] != "where"
                    or parts[7] != "id"
                    or parts[8] != "="
                ):
                    raise ValueError(
                        "Используй: update <таблица> set <колонка> = "
                        "<значение> where id = <id>"
                    )

                update(
                    metadata,
                    parts[1],
                    parts[9],
                    parts[3],
                    parts[5],
                )

            elif parts[0] == "delete":
                if (
                    len(parts) != 7
                    or parts[1] != "from"
                    or parts[3] != "where"
                    or parts[4] != "id"
                    or parts[5] != "="
                ):
                    raise ValueError(
                        "Используй: delete from <таблица> where id = <id>"
                    )

                delete(metadata, parts[2], parts[6])

            else:
                print("Неизвестная команда. Введи help.")

        except (KeyError, ValueError, FileNotFoundError) as error:
            print(f"Ошибка: {error}")