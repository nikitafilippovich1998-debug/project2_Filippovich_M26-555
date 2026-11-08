import shlex
import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

DB_FILE = "db_meta.json"


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("***База данных***")
    print_help()

    while True:
        user_input = prompt.string("Введите команду: ")
        
        # Разбиваем строку на команду и аргументы с помощью shlex
        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка в кавычках")
            continue
            
        if not args:
            continue

        command = args[0]

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            metadata = load_metadata(DB_FILE)
            if not metadata:
                print("Таблиц нет.")
            else:
                for table_name in metadata.keys():
                    print(f"- {table_name}")

        elif command == "create_table":
            if len(args) < 3:
                print("Ошибка: Недостаточно аргументов для create_table.")
                continue
            
            metadata = load_metadata(DB_FILE)
            table_name = args[1]
            columns = args[2:]
            
            result = create_table(metadata, table_name, columns)
            print(result)
            
            # Если таблица успешно создана (нет слова "Ошибка" в ответе)
            if "Ошибка" not in result:
                save_metadata(DB_FILE, metadata)

        elif command == "drop_table":
            if len(args) < 2:
                print("Ошибка: Недостаточно аргументов для drop_table.")
                continue
                
            metadata = load_metadata(DB_FILE)
            table_name = args[1]
            
            result = drop_table(metadata, table_name)
            print(result)
            
            if "Ошибка" not in result:
                save_metadata(DB_FILE, metadata)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")