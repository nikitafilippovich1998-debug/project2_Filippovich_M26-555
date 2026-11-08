def create_table(metadata, table_name, columns_list):
    if table_name in metadata:
        return f'Ошибка: Таблица "{table_name}" уже существует.'
    
    table_structure = {"ID": "int"}
    
    for column in columns_list:
        parts = column.split(":")
        if len(parts) != 2:
            return f"Ошибка: Неверный формат столбца {column}"
        
        col_name, col_type = parts
        if col_type not in ["int", "str", "bool"]:
            return f"Ошибка: Недопустимый тип данных {col_type}"
            
        table_structure[col_name] = col_type
        
    metadata[table_name] = table_structure
    return f'Таблица "{table_name}" успешно создана со столбцами: {", ".join([f"{k}:{v}" for k, v in table_structure.items()])}'


def drop_table(metadata, table_name):
    if table_name not in metadata:
        return f'Ошибка: Таблица "{table_name}" не существует.'
    
    del metadata[table_name]
    return f'Таблица "{table_name}" успешно удалена.'
