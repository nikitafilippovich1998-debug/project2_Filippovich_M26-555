def parse_condition(condition_str):
    """Превращает строку 'age = 28' в словарь {'age': '28'}"""
    if not condition_str:
        return {}
    
    # Разделяем по знаку равно и убираем лишние пробелы
    parts = condition_str.split("=")
    if len(parts) != 2:
        return None
        
    key = parts[0].strip()
    value = parts[1].strip().strip('"').strip("'") # Убираем кавычки у строк
    
    return {key: value}