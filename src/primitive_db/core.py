from primitive_db.decorators import handle_db_errors, confirm_action, log_time

@handle_db_errors
def create_table(metadata, table_name, columns_list):
    if table_name in metadata:
        return f'Ошибка: Таблица "{table_name}" уже существует.'
    
    table_structure = {"ID": "int"}
    for column in columns_list:
        parts = column.split(":")
        if len(parts) != 2:
            raise ValueError(f"Неверный формат столбца {column}")
        
        col_name, col_type = parts
        if col_type not in ["int", "str", "bool"]:
            raise ValueError(f"Недопустимый тип данных {col_type}")
            
        table_structure[col_name] = col_type
        
    metadata[table_name] = table_structure
    return f'Таблица "{table_name}" успешно создана.'


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    
    del metadata[table_name]
    return metadata, f'Таблица "{table_name}" успешно удалена.'


@handle_db_errors
@log_time
def insert(table_data, schema, values):
    if len(values) != len(schema) - 1:
        raise ValueError(f"Неверное количество значений. Ожидалось {len(schema) - 1}.")
    
    new_id = max([row["ID"] for row in table_data], default=0) + 1
    new_row = {"ID": new_id}
    
    col_names = [col for col in schema.keys() if col != "ID"]
    for i, col_name in enumerate(col_names):
        val = values[i]
        col_type = schema[col_name]
        
        if col_type == "int":
            val = int(val)
        elif col_type == "bool":
            val = True if str(val).lower() in ["true", "1"] else False
        elif col_type == "str":
            val = str(val)
            
        new_row[col_name] = val
        
    table_data.append(new_row)
    return table_data, f'Запись с ID={new_id} успешно добавлена.'


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    if not where_clause:
        return table_data
    
    result = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if str(row.get(key)) != str(val):
                match = False
                break
        if match:
            result.append(row)
    return result


@handle_db_errors
def update(table_data, set_clause, where_clause):
    count = 0
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if str(row.get(key)) != str(val):
                match = False
                break
        if match:
            for k, v in set_clause.items():
                if isinstance(row.get(k), int):
                    v = int(v)
                elif isinstance(row.get(k), bool):
                    v = True if str(v).lower() in ["true", "1"] else False
                row[k] = v
            count += 1
    return table_data, f"Обновлено записей: {count}"


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    initial_len = len(table_data)
    new_data = []
    for row in table_data:
        match = True
        for key, val in where_clause.items():
            if str(row.get(key)) != str(val):
                match = False
                break
        if not match:
            new_data.append(row)
            
    deleted_count = initial_len - len(new_data)
    return new_data, f"Удалено записей: {deleted_count}"