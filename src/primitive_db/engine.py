import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.constants import META_FILE
from primitive_db.core import create_table, delete, drop_table, insert, select, update
from primitive_db.decorators import create_cacher
from primitive_db.parser import parse_condition
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы>"
        "values (<значение1>, <значение2>, ...) "
        "- создать запись."
        )
    print("<command> select from <имя_таблицы> where"
    " <столбец> = <значение> - прочитать записи по условию.")
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where"
    " <столбец_условия> = <значение_условия> - обновить запись.")
    print("<command> delete from <имя_таблицы> " \
    "where <столбец> = <значение> - удалить запись.")
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("\nОбщие команды:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print("***База данных***")
    print_help()

    cache = create_cacher()

    while True:
        user_input = prompt.string("Введите команду: ")
        
        if not user_input.strip():
            continue

        # Заменяем скобки на пробелы для удобного разбора shlex
        # Например: values ("Sergei", 28) -> values Sergei, 28
        clean_input = user_input.replace("(", "").replace(")", "").replace(",", " ")
        
        try:
            args = shlex.split(clean_input)
        except ValueError:
            print("Ошибка: Незакрытая кавычка.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            break

        elif command == "help":
            print_help()

        elif command == "list_tables":
            metadata = load_metadata(META_FILE)
            if not metadata:
                print("Таблиц нет.")
            else:
                for table_name in metadata.keys():
                    print(f"- {table_name}")

        elif command == "create_table":
            if len(args) < 3:
                print("Ошибка: Недостаточно аргументов.")
                continue
            metadata = load_metadata(META_FILE)
            result = create_table(metadata, args[1], args[2:])
            print(result)
            if "Ошибка" not in result:
                save_metadata(META_FILE, metadata)

        elif command == "drop_table":
            if len(args) < 2:
                continue
            metadata = load_metadata(META_FILE)
            result = drop_table(metadata, args[1])
            print(result)
            if "Ошибка" not in result:
                save_metadata(META_FILE, metadata)

        elif command == "insert":
            # insert into users values (Sergei 28 true)
            if len(args) < 5 or args[1] != "into" or args[3] != "values":
                print("Ошибка: Неверный синтаксис. " \
                "Используйте: insert into <table> values (val1, val2)")
                continue
                
            table_name = args[2]
            metadata = load_metadata(META_FILE)
            
            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue
                
            table_data = load_table_data(table_name)
            values = args[4:]
            
            table_data, result = insert(table_data, metadata[table_name], values)
            print(result)
            if "Ошибка" not in result:
                save_table_data(table_name, table_data)

        elif command == "select":
            # select from users where age = 28
            if len(args) < 3 or args[1] != "from":
                print("Ошибка синтаксиса.")
                continue
            
            table_name = args[2]
            metadata = load_metadata(META_FILE)
            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue
                
            table_data = load_table_data(table_name)
            where_clause = None
            
            if "where" in args:
                where_idx = args.index("where")
                where_str = " ".join(args[where_idx+1:])
                where_clause = parse_condition(where_str)
                
            # Кэшируем по имени таблицы и условию
            cache_key = f"{table_name}_{where_clause}"
            results = cache(cache_key, lambda: select(table_data, where_clause))
            
            if not results:
                print("Записей не найдено.")
            else:
                pt = PrettyTable()
                pt.field_names = list(metadata[table_name].keys())
                for row in results:
                    pt.add_row([row.get(col) for col in pt.field_names])
                print(pt)

        elif command == "update":
            # update users set age = 29 where name = Sergei
            if len(args) < 5 or args[2] != "set" or "where" not in args:
                print("Ошибка синтаксиса.")
                continue
                
            table_name = args[1]
            metadata = load_metadata(META_FILE)
            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue
                
            table_data = load_table_data(table_name)
            
            where_idx = args.index("where")
            set_str = " ".join(args[3:where_idx])
            where_str = " ".join(args[where_idx+1:])
            
            set_clause = parse_condition(set_str)
            where_clause = parse_condition(where_str)
            
            table_data, result = update(table_data, set_clause, where_clause)
            print(result)
            if "Ошибка" not in result and result != "Обновлено записей: 0":
                save_table_data(table_name, table_data)

        elif command == "delete":
            # delete from users where age = 28
            if len(args) < 3 or args[1] != "from":
                print("Ошибка синтаксиса.")
                continue
                
            table_name = args[2]
            metadata = load_metadata(META_FILE)
            if table_name not in metadata:
                print(f"Ошибка: Таблица '{table_name}' не существует.")
                continue
                
            table_data = load_table_data(table_name)
            
            if "where" not in args:
                print("Ошибка: Отсутствует условие where.")
                continue
                
            where_idx = args.index("where")
            where_str = " ".join(args[where_idx+1:])
            where_clause = parse_condition(where_str)
            
            table_data, result = delete(table_data, where_clause)
            print(result)
            if "Ошибка" not in result and result != "Удалено записей: 0":
                save_table_data(table_name, table_data)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")